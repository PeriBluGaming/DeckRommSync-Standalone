# DeckRommSync - Standalone
DeckRomMSync - Standalone is a project that automatically synchronizes your ROMs from [RomM](https://github.com/rommapp/romm) to your Steam Deck. 
The games are automatically copied to the correct directory. [Retrodeck](https://retrodeck.net/) is required!
![DeckRomMSync](/docs/deckrommsync.png)

## Installation
1. Clone the Repository to your Steamdeck
   ```bash
    git clone https://github.com/PeriBluGaming/DeckRommSync-Standalone.git
   ```

2. Create a virtual environment and activate them
   ```bash
    python -m venv venv
    source venv/bin/activate
   ```

3. Install Requirements
   ```bash
    pip install -r requirements.txt
   ```

4. (Optional) Adjust the port in the config.json file. By default, the application runs on port 5000.

## Configuration
Now the installation is complete and you can start the application with following command. Make sure you have activate the environment, see Installation Point 2.
```bash
python3 app.py
```

After starting the application open a Browser `http://{ip-steamdeck}:5000` and click on `Config`.
Now you have to setup following Settings:

### RomM API Settings
**RomM API URL:** API URL from RomM `http://{ip-romm}:{port-romm}/api`\
**Username:**   your Username of RomM\
**Password:**   your Password of RomM

Press Save after entering the data. Then wait 2-3 minutes until the background worker has completed one cycle. Now refresh the Browser (F5)
(The Background Worker will fetch your Collections / Platforms / etc.)

### Configurate Platform Matching
After the Background Worker runs for the first time, you can see your Platforms and Collections on the Config-Page.\
**Steamdeck System Path:** Enter the path of your RetroDeck installation under `Steamdeck System Path`.

Below, you will see a table with all platforms.
For each platform, enter the folder name of your RetroDeck platform. For example: `Playstation 1 -> psx` and press Save.
**Note: You must press Save for every Platform your set!!!**
![Platform-Matching](/docs/platform_matching.png)

### Activate Collection Sync
To automatically sync the ROMs of one or more collections, you need to enable the collection.

On the Config page, you'll find the "Sync Collections" section. Here, your collections from RomM are displayed. You can enable/disable synchronization using the checkboxes.

**Note: Click Save after enabling it.**

After that, the synchronization will automatic run!
