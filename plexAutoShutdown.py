# pylint: disable=W0603,C0103,c-extension-no-member
"""Plex auto shutdown main script"""
import configparser
import msvcrt
import os
import threading
import time

import psutil
import win32api
from plexapi.server import PlexServer

os.system("TITLE Plex Auto-Shutdown")
config = configparser.ConfigParser()
config.read("config.ini")

baseurl = config["DEFAULT"]["Url"]
token = config["DEFAULT"]["Token"]
plex = PlexServer(baseurl, token)

MAX_IDLE_TIME = int(config["ADDITIONAL"]["MaxIdle"])
INTERVAL_DELAY = int(config["ADDITIONAL"]["IntervalDelay"])
SHUTDOWN_DELAY = int(config["ADDITIONAL"]["ShutdownDelay"])
SHUTDOWN_STATUS = False
ALLOW_EMOJIS = config["ADDITIONAL"].getboolean("ShowEmojis")

THREAD_RUNNING = True


def run_code_forever():
    """Runs code in loop"""
    while THREAD_RUNNING:
        time.sleep(INTERVAL_DELAY)
        start()


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


def start():
    """Main function"""
    global SHUTDOWN_STATUS
    if SHUTDOWN_STATUS:
        if check_if_idle_windows() < MAX_IDLE_TIME or check_if_are_active_sessions():
            print(render_emoji("❎") + "Auto-shutdown aborted")
            os.system("shutdown -a")
            SHUTDOWN_STATUS = False

    print("\nChecking status..")
    if check_if_idle_windows() < MAX_IDLE_TIME:
        print(render_emoji("❌") + "Computer is not in idle mode")
        return
    print(render_emoji("✔") + "Computer is in idle mode")

    if not check_if_transcoder_running():
        print(render_emoji("❌") + "Plex transcoder is running")
        return
    print(render_emoji("✔") + "Plex transcoder is not running")

    if check_if_are_active_sessions():
        print(render_emoji("❌") + "There are an active plex session")
        return
    print(render_emoji("✔") + "No plex session is active")

    if not SHUTDOWN_STATUS:
        print(
            render_emoji("✅")
            + "Auto-shutdown initiated, computer will shutdown in "
            + str(SHUTDOWN_DELAY)
            + " seconds"
        )
        os.system("shutdown -s -t " + str(SHUTDOWN_DELAY))
        SHUTDOWN_STATUS = True


if __name__ == "__main__":
    print(render_emoji("✅") + "Starting script...")
    print(render_emoji("🔔") + "Press any key to cancel")

    t1 = threading.Thread(target=run_code_forever)
    t2 = threading.Thread(target=msvcrt.getch)

    t1.start()
    t2.start()

    t2.join()
    THREAD_RUNNING = False
    print("\n" + render_emoji("❗") + "Closing script...")
    t1.join()
    print("\n" + render_emoji("💖") + "Thanks for using this script")
