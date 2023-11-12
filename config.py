""" Config file for PlexAutoShutdown """
import configparser
from os import path
import sys


def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)


CONFIG_FILE_PATH = "PlexAutoShutdownConfig.ini"
DEFAULT_COMPUTER_IDLE = 30
DEFAULT_INTERVAL_DELAY = 1
DEFAULT_SHUTDOWN_DELAY = 30
DEFAULT_PLEX_URL = "http://127.0.0.1:32400"
DEFAULT_PLEX_TOKEN = "Your Plex Token Here"


def load_config():
    """Loads the config file and returns the values"""
    if path.exists(CONFIG_FILE_PATH):
        print("Config file exists")
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        plex_url = config["DEFAULT"]["Url"]
        plex_token = config["DEFAULT"]["Token"]
        computer_idle = float(config["ADDITIONAL"]["MaxIdle"])
        interval_delay = float(config["ADDITIONAL"]["IntervalDelay"])
        shutdown_delay = float(config["ADDITIONAL"]["ShutdownDelay"])
        return plex_url, plex_token, computer_idle, interval_delay, shutdown_delay
    else:
        print("Config file does not exist")
        return (
            DEFAULT_PLEX_URL,
            DEFAULT_PLEX_TOKEN,
            DEFAULT_COMPUTER_IDLE,
            DEFAULT_INTERVAL_DELAY,
            DEFAULT_SHUTDOWN_DELAY,
        )


def write_config(plex_url, plex_token, computer_idle, interval_delay, shutdown_delay):
    """Writes the config file"""
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as config_file:
        config_file.write(
            f"""[DEFAULT]
Url = {plex_url}
; How to get token: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
Token = {plex_token}

[ADDITIONAL]
;Max computer idle time in seconds. Default: 30 minutes. Set to 0 to disable.
MaxIdle = {computer_idle}
;Delay between function interval in seconds. Default: 1 minute
IntervalDelay = {interval_delay}
;Delay in seconds, should be bigger than interval delay. Default: 30 minutes
ShutdownDelay = {shutdown_delay}
"""
        )
