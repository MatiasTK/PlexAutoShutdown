import os
import threading

import colorama
import psutil
import win32api
from plexapi.server import PlexServer

os.system('TITLE Plex Auto-Shutdown')

baseurl = input('Set Url: ')
token = input('Set Token: ')
plex = PlexServer(baseurl, token)
colorama.init()

MAX_IDLE_TIME = 1800
INTERVAL_DELAY = 60
SHUTDOWN_DELAY = 3600
SHUTDOWN_STATUS = False
ALLOW_EMOJIS = False


def set_interval(fn, sec):
    """ Repeatedly calls a function or executes with a fixed time delay between each call. """

    def func_wrapper():
        set_interval(fn, sec)
        fn()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def check_if_idle_windows():
    """ Returns computer idle time in seconds"""

    idle_time = (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0
    return idle_time


def check_if_transcoder_running():
    """ Returns true if plex is running and transcoder not """
    plex_running = False
    transcoder_running = False

    for p in psutil.process_iter():
        if p.name() == 'Plex Media Server.exe':
            plex_running = True
        if p.name() == 'Plex Transcoder.exe':
            transcoder_running = True

    return plex_running and not transcoder_running


def check_if_are_active_sessions():
    """ Returns true if there is any plex active session"""
    return len(plex.sessions()) > 0


def Start():
    global SHUTDOWN_STATUS, SHUTDOWN_DELAY
    if SHUTDOWN_STATUS:
        if check_if_idle_windows() < MAX_IDLE_TIME or check_if_are_active_sessions():
            print(colorama.Fore.YELLOW + 'Auto-shutdown aborted')
            os.system('shutdown -a')
            SHUTDOWN_STATUS = False

    print('Checking status..')
    if check_if_idle_windows() < MAX_IDLE_TIME:
        print(colorama.Fore.RED + 'Computer is in idle mode')
        return
    print(colorama.Fore.GREEN + 'Computer is in idle mode')

    if not check_if_transcoder_running():
        print(colorama.Fore.RED + 'Plex transcoder is not running')
        return
    print(colorama.Fore.GREEN + 'Plex transcoder is not running')

    if check_if_are_active_sessions():
        print(colorama.Fore.RED + 'No plex session is active')
        return
    print(colorama.Fore.GREEN + 'No plex session is active')

    if not SHUTDOWN_STATUS:
        print(colorama.Fore.YELLOW + 'Auto-shutdown initiated')
        os.system('shutdown -s -t ' + str(SHUTDOWN_DELAY))
        SHUTDOWN_STATUS = True


print(colorama.Fore.BLUE + 'Starting script...')
set_interval(Start, INTERVAL_DELAY)
