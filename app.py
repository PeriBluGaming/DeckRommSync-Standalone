from flask import Flask, redirect, render_template, request, jsonify, url_for
from django.shortcuts import render
from apscheduler.schedulers.background import BackgroundScheduler
from classes.RommAPIHelper import RommAPIHelper
from classes.DeckRommSyncDatabase import DeckRommSyncDatabase
from classes.BackgroundWorker import BackgroundWorker
import json
import os
import logging

# Logging für den Background Worker
background_logger = logging.getLogger("background_worker")
background_logger.setLevel(logging.INFO)
background_handler = logging.FileHandler("background_worker.log", encoding="utf-8")
background_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
background_handler.setFormatter(background_formatter)
background_logger.addHandler(background_handler)

app = Flask(__name__)

def run_background_task():
    """Ruft die `run()`-Methode der Hintergrundklasse auf."""
    # Background Worker erstellen
    bgWorker = BackgroundWorker("deckrommsync.db", background_logger)    
    background_logger.info("Background Task started...")
    bgWorker.sync_rommCollections()
    bgWorker.sync_copyRoms()    
    background_logger.info("Background Task finished...")


# Scheduler starten
scheduler = BackgroundScheduler()

# System-Logger einrichten
system_logger = logging.getLogger("system_logger")
system_logger.setLevel(logging.INFO)
system_handler = logging.FileHandler("system.log", encoding="utf-8")
system_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
system_handler.setFormatter(system_formatter)
system_logger.addHandler(system_handler)

def load_json_config(file_path="config.json"):
    """Lädt die Konfiguration aus der JSON-Datei."""
    system_logger.info("Load Config from File")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

@app.route('/')
def status():  
    system_logger.info("Status Page")  
    db = DeckRommSyncDatabase(app_config["database"].get("name", "deckrommsync.db"))
    collection_db_result = db.select_as_dict("collections", ['*'], 'collection_sync = 1')    
    collections = []
    for collection in collection_db_result:
        roms_in_collection = db.select_as_dict("roms", ['*'], 'collections_id = ?', (collection["collections_id"],))
        collection["roms"] = roms_in_collection    
        collections.append(collection)

    return render_template('status.html', status="Server läuft", version="1.0.0", collections=collections)

@app.route('/config', methods=['GET', 'POST'])
def config():
    db = DeckRommSyncDatabase(app_config["database"].get("name", "deckrommsync.db"))
    # Hole Config    
    config_result = db.select("config")    
    config_dict = {row[1]: row[2] for row in config_result}  # Wandelt die Liste in ein Dictionary um    
    
    # Hole Platform Matching
    platform_matching = db.select_as_dict("platforms_matching")

    # Hole Collections
    collections = db.select_as_dict("collections")    

    if request.method == 'POST':
        new_config = request.form.to_dict()
        # Save Config
    return render_template('config.html', config=config_dict, collections=collections, platform_matching=platform_matching)

# Update Romm API Settings
@app.route('/config/config_romm_api_settings', methods=['POST'])
def config_romm_api_settings():        

    # Create Database Object
    db = DeckRommSyncDatabase(app_config["database"].get("name", "deckrommsync.db"))

    # Update Config in Database
    db.update("config", {"config_value": request.form.get("romm_api_base_url")}, "config_key = ?", ("romm_api_base_url",))
    db.update("config", {"config_value": request.form.get("romm_username")}, "config_key = ?", ("romm_username",))
    db.update("config", {"config_value": request.form.get("romm_password")}, "config_key = ?", ("romm_password",))
    
    return redirect(url_for('config'))

# Update Collection Sync Settings
@app.route('/config/config_collection_sync_settings', methods=['POST']) 
def config_collection_sync_settings():

    # Create Database Object
    db = DeckRommSyncDatabase(app_config["database"].get("name", "deckrommsync.db"))

    # Get Collections IDs from Form
    collections_ids = request.form.getlist("collections_id")    

    for collections_id in collections_ids:           
        # Get Checkbox Value
        checkbox_value = "1" if f"collection_sync_{collections_id}" in request.form else "0"             
        db.update("collections", {"collection_sync": checkbox_value}, "collections_id = ?", (collections_id,))

    return redirect(url_for('config'))

# Update Platform Matching
@app.route('/config/config_platform_matching', methods=['POST'])
def config_platform_matching():    

    # Create Database Object
    db = DeckRommSyncDatabase(app_config["database"].get("name", "deckrommsync.db"))

    # Update Config in Database
    db.update("platforms_matching", {"steamdeck_platform_name": request.form.get("steamdeck_platform_name")}, "romm_platform_id = ?", (request.form.get("romm_platform_id"),))
    
    return redirect(url_for('config'))

# Update Steamdeck Platform Path
@app.route('/config/config_steamdeck_platform_path', methods=['POST'])
def config_steamdeck_platform_path():    

    # Create Database Object
    db = DeckRommSyncDatabase(app_config["database"].get("name", "deckrommsync.db"))

    # Update Config in Database
    db.update("config", {"config_value": request.form.get("steamdeck_path")}, "config_key = ?", ("steamdeck_retrodeck_path",))
    
    return redirect(url_for('config'))

# Status Dropdown: Reset Status
@app.route('/dropdown/reset_status', methods=['POST'])
def dropdown_reset_status():
    data = request.get_json()    

    # Create Database Object
    db = DeckRommSyncDatabase(app_config["database"].get("name", "deckrommsync.db"))

    # Update Rom Status
    db.update("roms", {"sync_status": "0"}, "roms_id = ?", (data['roms_id'],))
    
    return jsonify({"message": "Daten erfolgreich empfangen!", "data": data})

@app.route('/log')
def log():
    """Liest die Log-Datei zeilenweise ein und gibt eine Liste zurück."""
    """Liest die Log-Datei und teilt sie in Abschnitte, wenn 'Background Task finished...' vorkommt."""
    try:
        with open("background_worker.log", "r", encoding="utf-8") as file:
            logs = []
            current_section = []

            for line in file:
                if "Background Task started..." in line:
                    if current_section:
                        logs.append(current_section)  # Speichere die aktuelle Gruppe
                        current_section = []  # Starte eine neue Gruppe
                current_section.append(line.strip())  # Füge Zeile zur aktuellen Gruppe hinzu

            if current_section:  # Letzte Gruppe hinzufügen (falls vorhanden)
                logs.append(current_section)

            log_content = logs[::-1]  # Neueste Gruppe zuerst
    except FileNotFoundError:
        return [["Log-Datei nicht gefunden!"]]
    
    return render_template('log.html', log_groups=log_content)

@app.route('/scheduler-status', methods=['GET'])
def scheduler_status():
    return jsonify({"running": scheduler.running})

@app.route('/scheduler-click', methods=['GET'])
def scheduler_click():
    running = True
    if (scheduler.running):
        # scheduler.shutdown()
        scheduler.pause()
        running = False
    else:        
        # scheduler.add_job(run_background_task, "interval", minutes=1)  # Alle 2 Minuten
        # scheduler.start()
        scheduler.resume()
        running = True    

    return jsonify({"running": running, "shedular": scheduler.running})

if __name__ == '__main__':    
    system_logger.info("Flask-App started...")
    # Config
    global app_config
    app_config = load_json_config()  

    # DEBUG    
    scheduler.add_job(run_background_task, "interval", minutes=1)  # Alle 2 Minuten
    scheduler.start()  

    app.run(debug=True, use_reloader=False, host=app_config["server"].get("host", "localhost"), port=app_config["server"].get("port", 5000))
