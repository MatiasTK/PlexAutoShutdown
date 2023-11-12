""" This file contains all the functions related to the plex monitor and shutdown """
from __future__ import annotations

import os
import subprocess
from time import sleep
from typing import TYPE_CHECKING

from win11toast import toast

from idle import get_idle_duration

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
        try:
            # Run the tasklist command and capture the output
            result = subprocess.run(
                ["tasklist", "/fi", f"imagename eq {'Plex Media Server.exe'}"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Check if the process name is in the output
            if "Plex Media Server.exe".lower() in result.stdout.lower():
                plex_running = True

            subprocess.run(
                ["tasklist", "/fi", f"imagename eq {'Plex Transcoder.exe'}"],
                capture_output=True,
                text=True,
                check=True,
            )
            if "Plex Transcoder.exe".lower() in result.stdout.lower():
                transcoder_running = True
        except Exception as e:
            print(f"Error checking process: {e}")
            return False
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
        os.system(
            "shutdown -s -t " + str(int(self.minutes_to_seconds(time_in_minutes)))
        )
        self.shutdown_enabled = True

    def monitor_plex_and_shutdown(self):
        """Checks if there is any active plex session and if the computer is in idle mode, if both are true it will shutdown the computer after the given delay"""
        if not self.app.get_shutdown_status():
            return

        print("Monitoring...")
        max_idle_seconds = self.minutes_to_seconds(self.app.get_computer_idle())

        if self.shutdown_enabled:
            if (
                get_idle_duration() < max_idle_seconds
                or self.check_if_are_active_sessions()
            ):
                self.cancel_shutdown()

        if max_idle_seconds != 0:
            if get_idle_duration() < max_idle_seconds:
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
            self.monitor_plex_and_shutdown()
            sleep(self.minutes_to_seconds(self.app.get_interval_delay()))
