# Plex Auto-Shutdown

_Power off Windows when Plex server is not streaming._

### Requirements

- Plex media server 1.27 or greater
- Windows OS
- Python 3

### Usage

1. Install requirements

```powershell
pip install -r requirements.txt
```

2. Configure your server
   - Open `config.ini`
   - Replace values on `DEFAULT` section
   - Write your plex server url in `Url`
   - Write your [plex token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) in `Token`
3. Run the script

```powershell
python plexAutoShutdown.py
```

### How it works

1. The script checks if the computer is in idle mode using `MaxIdle` from config.
2. Check if plex transcoder is not running.
3. Check if there aren't any active session on plex.

If all of the above is true then the script sets a shutdown with a `ShutdownDelay` delay, while waiting for the shutdown if the script detects any new session or computer idle status reset then it cancels the shutdown.

### Additional Configurations

You can also change the following variables in the config.ini: `MAX_IDLE_TIME`, `INTERVAL_DELAY`, `SHUTDOWN_DELAY`, `SHOW_EMOJIS`.
