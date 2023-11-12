import configparser
from os import path

config_file_path = path.join(path.dirname(__file__), "PlexAutoShutdownConfig.ini")
default_computer_idle = 30
default_interval_delay = 1
default_shutdown_delay = 30
default_plex_url = "http://127.0.0.1:32400"
default_plex_token = "Your Plex Token Here"


def load_config():
    if path.exists(config_file_path):
        print("Config file exists")
        config = configparser.ConfigParser()
        config.read(config_file_path)
        plex_url = config["DEFAULT"]["Url"]
        plex_token = config["DEFAULT"]["Token"]
        computer_idle = float(config["ADDITIONAL"]["MaxIdle"])
        interval_delay = float(config["ADDITIONAL"]["IntervalDelay"])
        shutdown_delay = float(config["ADDITIONAL"]["ShutdownDelay"])
        return plex_url, plex_token, computer_idle, interval_delay, shutdown_delay
    else:
        print("Config file does not exist")
        return (
            None,
            default_computer_idle,
            default_plex_url,
            default_plex_token,
            default_interval_delay,
            default_shutdown_delay,
        )


def write_config(plex_url, plex_token, computer_idle, interval_delay, shutdown_delay):
    with open(config_file_path, "w", encoding="utf-8") as config_file:
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
