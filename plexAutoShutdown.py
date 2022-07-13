import configparser
import os
import threading

import psutil
import win32api
from plexapi.server import PlexServer

config = configparser.ConfigParser()
config.read('config.ini')

baseurl = config['DEFAULT']['Url']
token = config['DEFAULT']['Token']
plex = PlexServer(baseurl, token)

MAX_IDLE_TIME = int(config['ADDITIONAL']['MaxIdle'])
INTERVAL_DELAY = int(config['ADDITIONAL']['IntervalDelay'])
SHUTDOWN_DELAY = int(config['ADDITIONAL']['ShutdownDelay'])
SHUTDOWN_STATUS = False
ALLOW_EMOJIS = config['ADDITIONAL'].getboolean('ShowEmojis')


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


def renderEmoji(emoji):
    global ALLOW_EMOJIS
    if ALLOW_EMOJIS:
        return emoji + ' '
    return ''


def Start():
    global SHUTDOWN_STATUS, SHUTDOWN_DELAY
    if SHUTDOWN_STATUS:
        if check_if_idle_windows() < MAX_IDLE_TIME or check_if_are_active_sessions():
            print(renderEmoji('✅') + 'Auto-shutdown aborted')
            os.system('shutdown -a')
            SHUTDOWN_STATUS = False

    print('Checking status..')
    if check_if_idle_windows() < MAX_IDLE_TIME:
        print(renderEmoji('❌') + 'Computer is in idle mode')
        return
    print(renderEmoji('✔') + 'Computer is in idle mode')

    if not check_if_transcoder_running():
        print(renderEmoji('❌') + 'Plex transcoder is not running')
        return
    print(renderEmoji('✔') + 'Plex transcoder is not running')

    if check_if_are_active_sessions():
        print(renderEmoji('❌') + 'No plex session is active')
        return
    print(renderEmoji('✔') + 'No plex session is active')

    if not SHUTDOWN_STATUS:
        print(renderEmoji('❎') + 'Auto-shutdown initiated')
        os.system('shutdown -s -t ' + str(SHUTDOWN_DELAY))
        SHUTDOWN_STATUS = True


print(renderEmoji('✅') + 'Starting script...')
set_interval(Start, INTERVAL_DELAY)
