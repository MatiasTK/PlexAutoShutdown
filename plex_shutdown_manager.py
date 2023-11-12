""" This file contains all the functions related to the plex monitor and shutdown """
from __future__ import annotations

import os
from time import sleep
from typing import TYPE_CHECKING

from win32api import GetLastInputInfo, GetTickCount
from win32com.client import GetObject

from win11toast import toast

if TYPE_CHECKING:
    from app import App


class PlexShutdownManager:
    shutdown_enabled = False
    app: App = None

    def __init__(self):
        self.shutdown_enabled = False

    def check_if_are_active_sessions(self):
        """Returns true if there is any plex active session"""
        if self.app.get_plex_instance() is None:
            self.app.show_error(
                self.app,
                "Cannot check if there are active sessions, Plex connection error",
            )
            return False
        return len(self.app.get_plex_instance().sessions()) > 0

    def check_if_transcoder_running(self):
        """Returns true if plex is running and transcoder not"""
        if self.app.get_plex_instance() is None:
            self.app.show_error(
                self, "Cannot check if there are active sessions, Plex connection error"
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

    def minutes_to_seconds(self, minutes):
        """Converts minutes to seconds"""
        return minutes * 60

    def cancel_shutdown(self):
        """Cancels the shutdown"""
        print("Auto-shutdown aborted")
        os.system("shutdown -a")
        self.shutdown_enabled = False

    def activate_shutdown(self, time_in_minutes):
        """Activates the shutdown"""
        toast("Plex Auto Shutdown", "Auto-shutdown initiated")
        print(
            "Auto-shutdown initiated, computer will shutdown in "
            + str(time_in_minutes)
            + " seconds"
        )
        os.system("shutdown -s -t " + str(self.minutes_to_seconds(time_in_minutes)))
        self.shutdown_enabled = True

    def get_idle_time(self):
        """Returns computer idle time in seconds"""
        idle_time = (GetTickCount() - GetLastInputInfo()) / 1000.0
        return idle_time

    def monitor_plex_and_shutdown(self):
        """Checks if there is any active plex session and if the computer is in idle mode, if both are true it will shutdown the computer after the given delay"""
        print(f"SHUTDOWN STATUS {self.app.get_shutdown_status()}")
        if not self.app.get_shutdown_status():
            return

        print("Monitoring...")  # TODO: Quitar
        max_idle_seconds = self.minutes_to_seconds(self.app.get_computer_idle())

        if self.shutdown_enabled:
            if (
                self.get_idle_time() < max_idle_seconds
                or self.check_if_are_active_sessions()
            ):
                self.cancel_shutdown()

        if max_idle_seconds != 0:
            if self.get_idle_time() < max_idle_seconds:
                print("Computer is not in idle mode")
                return
            print("Computer is in idle mode")

        if not self.check_if_transcoder_running():
            print("Plex transcoder is running")
            return
        print("Plex transcoder is not running")

        if self.check_if_are_active_sessions():
            print("There are an active plex session")
            return
        print("No plex session is active")

        if not self.shutdown_enabled:
            self.activate_shutdown(self.app.get_shutdown_delay())

    def monitor_mainloop(self, tkinter_app: App):
        """Main loop for the monitor thread"""
        self.app = tkinter_app
        while True:
            print(
                f"MONITOR LOOP STARTED - Checking every {self.app.get_interval_delay()}"
            )  # TODO: Quitar
            self.monitor_plex_and_shutdown()
            sleep(self.minutes_to_seconds(self.app.get_interval_delay()))
