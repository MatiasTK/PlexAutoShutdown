# Plex Auto-Shutdown

_Power off Windows when Plex server is not streaming._

## Requirements

- Plex media server 1.27 or greater
- Windows OS
- Python 3

## Usage

1. Install requirements

   ```powershell
   pip install -r requirements.txt
   ```

2. Run the script & configure your server
   - Run the script `WinPlexAutoShutdown.py` or `WinPlexAutoShutdown.exe`
   - Open `config.ini`
   - Replace values on `DEFAULT` section
   - Write your plex server url in `Url`
   - Write your [plex token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) in `Token`
3. Run the script or just run `WinPlexAutoShutdown.exe` and it will run in the background.

   ```powershell
   python plexAutoShutdown.py
   ```

## How it works

1. The script checks if the computer is in idle mode using `MaxIdle` from config.
2. Check if plex transcoder is not running.
3. Check if there aren't any active session on plex.

If all of the above is true then the script sets a shutdown with a `ShutdownDelay` delay, while waiting for the shutdown if the script detects any new session or computer idle status reset then it cancels the shutdown.

## Additional Configurations

You can also change the following variables in the config.ini: `MAX_IDLE_TIME`, `INTERVAL_DELAY`, `SHUTDOWN_DELAY`, `SHOW_EMOJIS`.

## How to fix the top left notification

In order to fix the top left notification which says command prompt you should generate an Appllication User Model ID (AUMID) to do this:

1. You need to clone this repo to get the icons
2. **Make sure you have an icon.ico file inside the icons folder**
3. Run the following command

   ```powershell
   python register_hkey_aumid.py
   ```
