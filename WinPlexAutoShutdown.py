# pylint: disable=W0603,C0103,c-extension-no-member
"""Plex auto shutdown main script"""
import configparser
import os
import time
from datetime import datetime
from sys import exit
import psutil
import win32api
from plexapi.server import PlexServer
from windows_toasts import (
    AudioSource,
    InteractableWindowsToaster,
    ToastActivatedEventArgs,
    ToastAudio,
    ToastButton,
    ToastDisplayImage,
    ToastImageAndText1,
)

from helper import long_running, check_aumid

DIR_PATH = os.path.dirname(__file__)
ICON_PATH = DIR_PATH + r"/plex.png"

if check_aumid("WinPlexAutoShutdown"):
    toaster = InteractableWindowsToaster("Plex Auto Shutdown", "WinPlexAutoShutdown")
else:
    toaster = InteractableWindowsToaster("Plex Auto Shutdown")

activatedScript = ToastImageAndText1()
activatedScript.AddImage(ToastDisplayImage.fromPath(ICON_PATH))

activatedScript.SetAudio(ToastAudio(AudioSource.Reminder, looping=False))
activatedScript.AddAction(ToastButton("Click here to cancel", "response=cancel"))

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
;Change to true if your terminal supports emoji display only works in terminal mode. Default: false
ShowEmojis = false"""

TOAST_DELAY_TIME = 5  # In seconds


def load_config(configurations):
    if os.path.exists(DEFAULT_CONFIG_FILE_NAME):
        configurations.read(DEFAULT_CONFIG_FILE_NAME)
    else:
        with open(DEFAULT_CONFIG_FILE_NAME, "w", encoding="utf-8") as configfile:
            configfile.write(DEFAULT_CONFIG_FILE)
        reloadToast = ToastImageAndText1()
        reloadToast.AddImage(ToastDisplayImage.fromPath(ICON_PATH))
        reloadToast.SetBody(
            "Config file created. Please fill it and start script again"
        )
        reloadToast.SetAudio(ToastAudio(AudioSource.IM, looping=False))
        toaster.show_toast(reloadToast)
        time.sleep(TOAST_DELAY_TIME)
        exit()


load_config(config)

baseurl = config["DEFAULT"]["Url"]
token = config["DEFAULT"]["Token"]
plex = PlexServer(baseurl, token)

MAX_IDLE_TIME = int(config["ADDITIONAL"]["MaxIdle"])
INTERVAL_DELAY = int(config["ADDITIONAL"]["IntervalDelay"])
SHUTDOWN_DELAY = int(config["ADDITIONAL"]["ShutdownDelay"])
ALLOW_EMOJIS = config["ADDITIONAL"].getboolean("ShowEmojis")

SHUTDOWN_STATUS = False


RUNNING = True


def cancel_script(activatedEventArgs: ToastActivatedEventArgs):
    """cancels shutdown and closes script"""
    global RUNNING

    if activatedEventArgs.arguments == "response=cancel":
        os.system("shutdown -a")
        cancelToast = ToastImageAndText1()
        cancelToast.AddImage(ToastDisplayImage.fromPath(ICON_PATH))
        cancelToast.SetBody("Auto-shutdown aborted")
        cancelToast.SetAudio(ToastAudio(AudioSource.IM, looping=False))
        toaster.show_toast(cancelToast)
        RUNNING = False


activatedScript.on_activated = cancel_script


def check_if_idle_windows():
    """Returns computer idle time in seconds"""

    idle_time = (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0
    return idle_time


def check_if_transcoder_running():
    """Returns true if plex is running and transcoder not"""
    plex_running = False
    transcoder_running = False

    for process in psutil.process_iter():
        if process.name() == "Plex Media Server.exe":
            plex_running = True
        if process.name() == "Plex Transcoder.exe":
            transcoder_running = True

    return plex_running and not transcoder_running


def check_if_are_active_sessions():
    """Returns true if there is any plex active session"""
    return len(plex.sessions()) > 0


def render_emoji(emoji):
    """Returns emoji if ALLOW_EMOJIS is true"""
    if ALLOW_EMOJIS:
        return emoji + " "
    return ""


def get_current_time():
    """Returns current time"""
    return datetime.now().strftime("%I:%M:%S %p  ")


def start():
    """Main function"""
    global SHUTDOWN_STATUS
    if SHUTDOWN_STATUS:
        if check_if_idle_windows() < MAX_IDLE_TIME or check_if_are_active_sessions():
            print(get_current_time() + render_emoji("❎") + "Auto-shutdown aborted")
            os.system("shutdown -a")
            SHUTDOWN_STATUS = False

    print("\nChecking status..")
    if MAX_IDLE_TIME != 0:
        if check_if_idle_windows() < MAX_IDLE_TIME:
            print(
                get_current_time() + render_emoji("❌") + "Computer is not in idle mode"
            )
            return
        print(get_current_time() + render_emoji("✔") + "Computer is in idle mode")

    if not check_if_transcoder_running():
        print(get_current_time() + render_emoji("❌") + "Plex transcoder is running")
        return
    print(get_current_time() + render_emoji("✔") + "Plex transcoder is not running")

    if check_if_are_active_sessions():
        print(
            get_current_time() + render_emoji("❌") + "There are an active plex session"
        )
        return
    print(get_current_time() + render_emoji("✔") + "No plex session is active")

    if not SHUTDOWN_STATUS:
        print(
            get_current_time()
            + render_emoji("✅")
            + "Auto-shutdown initiated, computer will shutdown in "
            + str(SHUTDOWN_DELAY)
            + " seconds"
        )
        activatedScript.SetBody("Shuting down computer in " + str(SHUTDOWN_DELAY))
        toaster.show_toast(activatedScript)

        os.system("shutdown -s -t " + str(SHUTDOWN_DELAY))
        SHUTDOWN_STATUS = True


def run_script():
    """Runs script"""
    while RUNNING:
        start()
        time.sleep(INTERVAL_DELAY)


@long_running  # To avoid windows go to sleep
def main():
    """Main function"""
    print(render_emoji("✅") + "Starting script...")
    print(render_emoji("🔔") + "Press any key to cancel")

    activatedScript.SetBody("Script started")
    toaster.show_toast(activatedScript)

    run_script()

    print("\n" + render_emoji("❌") + "Script canceled")


main()
