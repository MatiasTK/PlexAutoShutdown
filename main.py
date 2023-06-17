"""Plex auto shutdown main script"""
import configparser
import os
import time
from datetime import datetime

import win32api
import win32com.client
from PIL import Image
from plexapi.server import PlexServer
from pystray import Icon as icon
from pystray import Menu as menu
from pystray import MenuItem as item
from win11toast import toast

from utils.helper import long_running

# ICONS
DIR_PATH = os.path.dirname(__file__)
ICON = Image.open(DIR_PATH + r"\icons\plex_final.png")
ICO = DIR_PATH + r"\icons\plex.ico"

# CONFIG
config = configparser.ConfigParser()
DEFAULT_CONFIG_FILE_NAME = "config.ini"
DEFAULT_CONFIG_FILE = """[DEFAULT]
Url = http://127.0.0.1:32400
; How to get token: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
Token =

[ADDITIONAL]
;Max computer idle time in seconds. Default: 1800 ( 30 minutes ). Set to 0 to disable.
MaxIdle = 1800
;Delay between function interval in seconds. Default: 60 ( 1 minute )
IntervalDelay = 60
;Delay in seconds, should be bigger than interval delay. Default: 1800 ( 30 minutes )
ShutdownDelay = 1800
"""

class PlexAutoShutdown:
    """Main class"""

    def __init__(self, plex: PlexServer, shutdown_delay=1800, max_idle_time=1800, interval_delay=60):
        self.__plex = plex
        self.shutdown_delay = shutdown_delay
        self.max_idle_time = max_idle_time
        self.interval_delay = interval_delay
        self.__shutdown_status = False
        self.__running = True
        self.__icon = icon(
            "WinPlexAutoShutdown",
            ICON,
            "Windows Plex Auto Shutdown",
            menu=menu(
                item(text="Status: OFF", action=None),
                menu.SEPARATOR,
                item("Cancel Shutdown", action=self.__cancel_shutdown),
                menu.SEPARATOR,
                item("Exit", action=self.__close_from_tray),
            ),
        )
        toast("Plex Auto-Shutdown","Script started in tray", icon={"src": ICO, "placement": "appLogoOverride"})
        self.__icon.run_detached()

    def __update_menu(self):
        self.__icon.menu = menu(
            item(text=f"Status: {'ON' if self.__shutdown_status else 'OFF'}", action=None),
            menu.SEPARATOR,
            item("Cancel Shutdown", action=self.__cancel_shutdown),
            menu.SEPARATOR,
            item("Exit", action=self.__close_from_tray),
        )

    def __get_current_time(self):
        """Returns current time"""
        return datetime.now().strftime("%I:%M:%S %p  ")

    def __check_if_idle_windows(self):
        """Returns computer idle time in seconds"""

        idle_time = (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0
        return idle_time

    def __check_if_are_active_sessions(self):
        """Returns true if there is any plex active session"""
        return len(self.__plex.sessions()) > 0

    def __check_if_transcoder_running(self):
        """Returns true if plex is running and transcoder not"""
        plex_running = False
        transcoder_running = False

        wmi = win32com.client.GetObject("winmgmts:")
        processes = wmi.InstancesOf("Win32_Process")

        for process in processes:
            if process.Properties_("Name").Value == "Plex Media Server.exe":
                plex_running = True
            if process.Properties_("Name").Value == "Plex Transcoder.exe":
                transcoder_running = True

        return plex_running and not transcoder_running

    def __run_in_background(self):

        # Cancel shutdown if there is any active session or computer is not idle
        if self.__shutdown_status:
            if self.__check_if_idle_windows() < self.max_idle_time or self.__check_if_are_active_sessions():
                print(self.__get_current_time() + "Auto-shutdown aborted")
                toast("Plex Auto-Shutdown","Auto-shutdown aborted", icon={"src": ICO, "placement": "appLogoOverride"})
                os.system("shutdown -a")
                self.__shutdown_status = False

        print("\nChecking status..")
        if self.max_idle_time != 0:
            if self.__check_if_idle_windows() < self.max_idle_time:
                print(
                    self.__get_current_time() + "Computer is not in idle mode"
                )
                return
            print(self.__get_current_time()+ "Computer is in idle mode")

        if not self.__check_if_transcoder_running():
            print(self.__get_current_time() + "Plex transcoder is running")
            return
        print(self.__get_current_time() + "Plex transcoder is not running")

        if self.__check_if_are_active_sessions():
            print(
                self.__get_current_time() + "There are an active plex session"
            )
            return
        print(self.__get_current_time() + "No plex session is active")

        if not self.__shutdown_status:
            print(
                self.__get_current_time()
                + "Auto-shutdown initiated, computer will shutdown in "
                + str(self.shutdown_delay)
                + " seconds"
            )
            toast("Plex Auto-Shutdown",f"Shuting down computer in {str(self.shutdown_delay)}", icon={"src": ICO, "placement": "appLogoOverride"})

            os.system("shutdown -s -t " + str(self.shutdown_delay))
            self.__shutdown_status = True

    def start(self):
        """ Starts the mainloop of the program """
        while self.__running:
            self.__run_in_background()
            self.__update_menu()
            time.sleep(self.interval_delay)

    def __cancel_shutdown(self):
        if self.__shutdown_status:
            os.system("shutdown -a")
            toast("Plex Auto-Shutdown","Shutdown Aborted!", icon={"src": ICO, "placement": "appLogoOverride"})

    def __close_from_tray(self):
        if self.__shutdown_status:
            self.__cancel_shutdown()
        self.__running = False
        toast("Plex Auto-Shutdown","Closing program...", icon={"src": ICO, "placement": "appLogoOverride"})
        self.__icon.stop()


def load_config(configurations):
    """ Loads initial config or creates one if not exists """
    if os.path.exists(DEFAULT_CONFIG_FILE_NAME):
        configurations.read(DEFAULT_CONFIG_FILE_NAME)
        base_url = configurations["DEFAULT"]["Url"]
        token = configurations["DEFAULT"]["Token"]
        max_idle_time = int(config["ADDITIONAL"]["MaxIdle"])
        interval_delay = int(config["ADDITIONAL"]["IntervalDelay"])
        shutdown_delay = int(config["ADDITIONAL"]["ShutdownDelay"])
        return base_url, token, max_idle_time, interval_delay, shutdown_delay
    else:
        with open(DEFAULT_CONFIG_FILE_NAME, "w", encoding="utf-8") as configfile:
            configfile.write(DEFAULT_CONFIG_FILE)
        toast("Plex Auto-Shutdown","Config file created. Please fill it and start script again", icon={"src": ICO, "placement": "appLogoOverride"})
        return "", "", None, None, None

@long_running  # To avoid windows go to sleep
def main():
    """Main function"""

    plex_url, plex_token, idle_time, interval_execution, shutdown_delay = load_config(config)

    if plex_url == "" or plex_token == "":
        print("Please fill config file")
        return

    try:
        plex = PlexServer(plex_url, plex_token)
    except ConnectionError:
        print("Error connecting to plex server, check if plex is running and config file is correct")
        return

    print("Starting script...")

    PlexAutoShutdown(plex, shutdown_delay, idle_time, interval_execution).start()

    print("\n" + "Script canceled")

if __name__ == "__main__":
    main()
