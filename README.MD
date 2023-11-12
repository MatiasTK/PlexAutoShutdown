# Plex Auto-Shutdown

_Power off Windows when Plex server is not streaming._

## Features

- GUI interface
- Notifications when the app is running
- Tray icon on close
- Configurable

## Requirements

- Plex media server 1.27 or greater
- Windows OS
- Python 3

## Usage

1. Download the latest release from [here](https://github.com/MatiasTK/PlexAutoShutdown/releases/latest).
2. Place `Plex.Auto.Shutdown.exe` somewhere in your computer.
3. Open `Plex.Auto.Shutdown.exe` and insert your Plex server url and token, [How to find your token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
4. Change the other settings if you want.
5. Click on `Apply Settings`.
6. Start the script by clicking on `Toggle Auto Shutdown`.

## Using python script

1. Install requirements

   ```powershell
   pip install -r requirements.txt
   ```

2. Run the script

   ```powershell
   python Plex.Auto.Shutdown.py
   ```

3. Insert your Plex server url and token, [How to find your token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
4. Change the other settings if you want.
5. Click on `Apply Settings`.
6. Start the script by clicking on `Toggle Auto Shutdown`.

## How it works

1. The script checks if the computer is in idle mode using `MaxIdle` from config.
2. Check if Plex transcoder is not running.
3. Check if there aren't any active session on Plex.

If all of the above is true then the script sets a shutdown with a `ShutdownDelay` delay, while waiting for the shutdown if the script detects any new session or computer idle status reset then it cancels the shutdown.

## Additional Configurations

You can also change the following variables in the config.ini: `MAX_IDLE_TIME`, `INTERVAL_DELAY`, `SHUTDOWN_DELAY`.
