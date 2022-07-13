import os
import threading

import colorama
import psutil
import win32api
from plexapi.server import PlexServer

baseurl = 'http://127.0.0.1:32400'  # Your plex url here
token = ''  # Your plex token here
plex = PlexServer(baseurl, token)
colorama.init()

MAX_IDLE_TIME = 1800  # Max computer idle time in seconds. Default: 1800 ( 30 minutes )
INTERVAL_DELAY = 60  # Delay between function interval in seconds. Default: 60
SHUTDOWN_DELAY = 90  # Delay in seconds, should be bigger than interval delay. Default: 90
SHUTDOWN_STATUS = False


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
    return len(plex.sessions()) >= 0


def Start():
    global SHUTDOWN_STATUS, SHUTDOWN_DELAY
    if SHUTDOWN_STATUS:
        if check_if_idle_windows() < MAX_IDLE_TIME:
            print(colorama.Fore.GREEN + 'Auto-shutdown aborted')
            os.system('shutdown -a')
            SHUTDOWN_STATUS = False

    print(colorama.Fore.BLUE + 'Checking status..')
    if check_if_idle_windows() < MAX_IDLE_TIME:
        print(colorama.Fore.BLUE + 'Computer not idle')
        return
    print(colorama.Fore.BLUE + 'Computer idle')

    if not check_if_transcoder_running():
        print(colorama.Fore.BLUE + 'Plex running')
        return
    print(colorama.Fore.BLUE + 'Plex transcoder not running')

    if not check_if_are_active_sessions():
        print(colorama.Fore.BLUE + 'Plex active')
        return
    print(colorama.Fore.BLUE + 'No plex active sessions')

    if not SHUTDOWN_STATUS:
        print(colorama.Fore.RED + 'Auto-shutdown initiated')
        os.system('shutdown -s -t ' + str(SHUTDOWN_DELAY))
        SHUTDOWN_STATUS = True


set_interval(Start, INTERVAL_DELAY)
