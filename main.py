from customtkinter import *
from pystray import MenuItem as item
import pystray
from PIL import Image
import webbrowser
from os import path
from plexapi.server import PlexServer
import configparser
import time

from win32api import GetTickCount, GetLastInputInfo
from win32com.client import GetObject
import threading


shutdown_switch_enabled = False
config_file_path = path.join(path.dirname(__file__), "PlexAutoShutdownConfig.ini")
shutdown_switch_ending_enabled = False  # Yet to be implemented
plex_url = "http://127.0.0.1:32400"
plex_token = ""
computer_idle = 30
interval_delay = 1
shutdown_delay = 30
plex: PlexServer or None = None
shutdown_enabled = False
background_running = True


def load_config():
    global plex_url, plex_token, computer_idle, interval_delay, shutdown_delay, plex
    if path.exists(config_file_path):
        print("Config file exists")
        config = configparser.ConfigParser()
        config.read(config_file_path)
        plex_url = config["DEFAULT"]["Url"]
        plex_token = config["DEFAULT"]["Token"]
        computer_idle = int(config["ADDITIONAL"]["MaxIdle"])
        interval_delay = int(config["ADDITIONAL"]["IntervalDelay"])
        shutdown_delay = int(config["ADDITIONAL"]["ShutdownDelay"])
        plex = PlexServer(plex_url, plex_token)


def write_config():
    global config_file_path, plex_url, plex_token, computer_idle, interval_delay, shutdown_delay
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


load_config()

win = CTk(fg_color="#2b2b2b")
win.title("Plex Auto Shutdown")
win.resizable(0, 0)


def get_idle_time():
    """Returns computer idle time in seconds"""

    idle_time = (GetTickCount() - GetLastInputInfo()) / 1000.0
    return idle_time


def check_if_are_active_sessions():
    """Returns true if there is any plex active session"""
    if plex is None:
        show_error(
            win, "Cannot check if there are active sessions, Plex connection error"
        )
        return False
    return len(plex.sessions()) > 0


def check_if_transcoder_running():
    """Returns true if plex is running and transcoder not"""
    if plex is None:
        show_error(
            win, "Cannot check if there are active sessions, Plex connection error"
        )
        return False
    plex_running = False
    transcoder_running = False

    wmi = GetObject("winmgmts:")
    processes = wmi.InstancesOf("Win32_Process")

    for process in processes:
        if process.Properties_("Name").Value == "Plex Media Server.exe":
            plex_running = True
        if process.Properties_("Name").Value == "Plex Transcoder.exe":
            transcoder_running = True

    return plex_running and not transcoder_running


def quit_window(icon):
    """Ends the program"""
    global background_running
    background_running = False
    icon.stop()
    win.quit()


def show_window(icon):
    """Deiconifies the window"""
    icon.stop()
    win.after(0, win.deiconify())


def hide_window():
    """Hides the window and shows the icon in the system tray"""
    win.withdraw()
    image = Image.open("./icons/plex.ico")
    menu = (item("Show", show_window), item("Quit", quit_window))
    icon = pystray.Icon("PlexAutoShutdown", image, "Plex Auto Shutdown", menu)
    icon.run()


def show_success(frame, message):
    """Shows a success message for 5 seconds"""
    success_label = CTkLabel(
        frame,
        text=f"Success: {message}",
        text_color="green",
        font=("Arial", 12, "bold"),
    )
    success_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
    win.after(5000, success_label.destroy)


def show_error(frame, error):
    """Shows an error message for 5 seconds"""
    error_label = CTkLabel(
        frame, text=f"Error: {error}", text_color="red", font=("Arial", 12, "bold")
    )
    error_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
    win.after(5000, error_label.destroy)


def visit_web(url):
    """Opens a web browser with the given url"""
    webbrowser.open(url)


def minutes_to_seconds(minutes):
    """Converts minutes to seconds"""
    return minutes * 60


def minutes_to_milliseconds(minutes):
    """Converts minutes to milliseconds"""
    return minutes * 60000


def apply_settings(url_entry, token_entry, shutdown_delay_entry, interval_delay_entry):
    """Applies the settings to the program"""
    global shutdown_switch_enabled, shutdown_switch_ending_enabled, plex_url, plex_token, computer_idle, interval_delay, shutdown_delay, plex
    plex_token = token_entry.get()
    if plex_token == "":
        show_error(win, "Token can't be empty")
        return
    # TODO: Faltan verificaciones
    shutdown_switch_enabled = False
    shutdown_switch_ending_enabled = False
    plex_url = url_entry.get()
    computer_idle = int(shutdown_delay_entry.get())
    interval_delay = int(interval_delay_entry.get())
    shutdown_delay = int(shutdown_delay_entry.get())
    try:
        plex = PlexServer(plex_url, plex_token)
        write_config()
        show_success(win, "Settings applied")
    except ConnectionError:
        show_error(win, "Connection error")
        return


def toggle_auto_shutdown(label):
    """Toggles the auto shutdown switch, if it's enabled it will stop the auto shutdown"""
    global shutdown_switch_enabled
    shutdown_switch_enabled = not shutdown_switch_enabled
    if shutdown_switch_enabled:
        show_success(win, "Auto Shutdown is now ON")
        label.configure(text="Toggle Auto Shutdown ON")
    else:
        os.system("shutdown -a")
        show_success(win, "Auto Shutdown is now OFF")
        label.configure(text="Toggle Auto Shutdown OFF")


def monitor_plex_and_shutdown():
    """Checks if there is any active plex session and if the computer is in idle mode, if both are true it will shutdown the computer after the given delay"""
    global shutdown_switch_enabled, computer_idle, shutdown_delay, shutdown_enabled
    if not shutdown_switch_enabled:
        return
    print("Monitoring...")  # TODO: Quitar
    max_idle_seconds = minutes_to_seconds(computer_idle)
    if shutdown_enabled:
        if get_idle_time() < max_idle_seconds or check_if_are_active_sessions():
            print("Auto-shutdown aborted")
            """ toast(
                "Plex Auto-Shutdown",
                "Auto-shutdown aborted",
                icon={"src": ICO, "placement": "appLogoOverride"},
            ) """
            os.system("shutdown -a")
            shutdown_enabled = False

    if max_idle_seconds != 0:
        if get_idle_time() < max_idle_seconds:
            print("Computer is not in idle mode")
            return
        print("Computer is in idle mode")

    if not check_if_transcoder_running():
        print("Plex transcoder is running")
        return
    print("Plex transcoder is not running")

    if check_if_are_active_sessions():
        print("There are an active plex session")
        return
    print("No plex session is active")

    if not shutdown_enabled:
        print(
            "Auto-shutdown initiated, computer will shutdown in "
            + str(shutdown_delay)
            + " seconds"
        )
        """ toast(
            "Plex Auto-Shutdown",
            f"Shuting down computer in {str(shutdown_delay)}",
            icon={"src": ICO, "placement": "appLogoOverride"},
        ) """

        os.system("shutdown -s -t " + str(minutes_to_seconds(shutdown_delay)))
        shutdown_enabled = True


def monitor_mainloop():
    """Main loop of the program background thread"""
    print("MONITOR LOOP STARTED")  # TODO: Quitar
    monitor_plex_and_shutdown()
    time.sleep(minutes_to_seconds(interval_delay))
    if background_running:
        monitor_mainloop()


win.protocol("WM_DELETE_WINDOW", hide_window)

#! USER INTERFACE
label = CTkLabel(
    win,
    text=f"Auto Shutdown is currently: {'ON' if shutdown_switch_enabled else 'OFF'}",
)
label.grid(row=0, column=1, padx=10, pady=(20, 10))

button = CTkButton(
    win, text="Toggle Auto Shutdown", command=lambda: toggle_auto_shutdown(label)
)
button.grid(row=0, column=0, padx=10, pady=(20, 10))

shutdown_on_show_end_button = CTkButton(
    win,
    text="Shutdown when show ends",
    command=lambda: show_error(win, "Not implemented yet"),
)
shutdown_on_show_end_button.grid(row=1, column=0, padx=10, pady=10)
shutdown_on_show_end_label = CTkLabel(
    win,
    text=f"Shutdown when show ends is: {'ON' if shutdown_switch_ending_enabled else 'OFF'}",
)
shutdown_on_show_end_label.grid(row=1, column=1, padx=10, pady=10)

url_label = CTkLabel(win, text="Plex URL")
url_label.grid(row=2, column=0, padx=10, pady=(10, 0))
url_entry = CTkEntry(win)
url_entry.grid(row=3, column=0, padx=10, pady=(0, 10))
url_entry.insert(0, plex_url)

token_label = CTkLabel(win, text="Plex Token")
token_label.grid(row=2, column=1, padx=10, pady=(10, 0))
token_entry = CTkEntry(win)
token_entry.grid(row=3, column=1, padx=10, pady=(0, 10))
token_entry.insert(0, plex_token)

shutdown_delay_label = CTkLabel(win, text="Shutdown after (minutes)")
shutdown_delay_label.grid(row=4, column=0, padx=10, pady=(10, 0))
shutdown_delay_entry = CTkEntry(win)
shutdown_delay_entry.grid(row=5, column=0, padx=10, pady=(0, 10))
shutdown_delay_entry.insert(0, shutdown_delay)

interval_delay_label = CTkLabel(win, text="Check every (minutes)")
interval_delay_label.grid(row=4, column=1, padx=10, pady=(10, 0))
interval_delay_entry = CTkEntry(win)
interval_delay_entry.grid(row=5, column=1, padx=10, pady=(0, 10))
interval_delay_entry.insert(0, interval_delay)

apply_settings_button = CTkButton(
    win,
    text="Apply Settings",
    command=lambda: apply_settings(
        url_entry, token_entry, shutdown_delay_entry, interval_delay_entry
    ),
)
apply_settings_button.grid(row=6, column=0, columnspan=6, padx=10, pady=10)

author_label = CTkLabel(
    win, text="Made by MatiasTK", font=("Arial", 10, "bold"), cursor="hand2"
)
author_label.bind("<Button-1>", lambda e: visit_web("https://github.com/MatiasTK"))
author_label.grid(row=8, column=0, padx=10, pady=10)

how_to_get_token_label = CTkLabel(
    win, text="How to get your Plex Token?", font=("Arial", 10, "bold"), cursor="hand2"
)
how_to_get_token_label.bind(
    "<Button-1>",
    lambda e: visit_web(
        "https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/"
    ),
)
how_to_get_token_label.grid(row=8, column=1, padx=10, pady=10)

background_thread = threading.Thread(target=monitor_mainloop)
win.after(1000, background_thread.start)
win.mainloop()
