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
    * Change ```baseurl``` to your plex url and ``token`` for
      your [plex token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
3. Run the script

```powershell
python plexAutoShutdown.py
```

### Additional Configurations

You can also change the following variables: ``MAX_IDLE_TIME``, ``INTERVAL_DELAY``, ``SHUTDOWN_DELAY``. 