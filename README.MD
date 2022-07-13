# Plex Auto-Shutdown

_Power off Windows when Plex server is not streaming._

### Requirements

* Plex media server 1.27.2
* Windows OS
* Python 3

### Usage

1. Install requirements

````powershell
pip install -r requirements.txt
````

2. Configure your server
   * Open `config.ini`
   * Replace values on `DEFAULT` section
   * Write your plex server url in `Url`
   * Write your [plex token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) in `Token`
4. Run the script

```powershell
python plexAutoShutdown.py
```

Or just run `start.bat`

### Additional Configurations

You can also change the following variables in the config.ini: ``MAX_IDLE_TIME``, ``INTERVAL_DELAY``, ``SHUTDOWN_DELAY``. 