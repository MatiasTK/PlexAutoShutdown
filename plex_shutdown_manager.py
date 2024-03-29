""" This file contains all the functions related to the Plex monitor and shutdown """
from __future__ import annotations

import subprocess
from time import sleep
from typing import TYPE_CHECKING

from win11toast import toast

from idle import get_idle_duration, WindowsInhibitor

if TYPE_CHECKING:
    from app import App

ACTIVATED_SHUTDOWN = 1
CANCELED_SHUTDOWN = -1
NO_ACTIVATION = 0


class PlexShutdownManager:
    """This class contains all the functions related to the Plex monitor and shutdown"""

    shutdown_enabled: bool
    app: App

    def __init__(self, app: App):
        self.shutdown_enabled = False
        self.app = app

    def check_if_are_active_sessions(self):
        """Returns true if there is any Plex active session"""
        if not self.app:
            return False

        if self.app.get_plex_instance() is None:
            self.app.show_error(
                self.app,
                "Cannot check if there are active sessions, Plex connection error",
            )
            return False
        return len(self.app.get_plex_instance().sessions()) > 0

    def check_if_transcoder_running(self):
        """Returns true if Plex is running and transcoder not"""
        if not self.app:
            return False
        if self.app.get_plex_instance() is None:
            self.app.show_error(
                self, "Cannot check if there are active sessions, Plex connection error"
            )
            return False
        plex_running = False
        transcoder_running = False
        try:
            # Run the task list command and capture the output
            result = subprocess.run(
                ["tasklist", "/fi", "imagename eq Plex*"],
                capture_output=True,
                text=True,
                shell=True,
                check=True,
            )
            # Check if the process name is in the output
            if "Plex Media Server.exe".lower() in result.stdout.lower():
                plex_running = True
            if "Plex Transcoder.exe".lower() in result.stdout.lower():
                transcoder_running = True
        except subprocess.CalledProcessError as e:
            print(f"Error checking process: {e}")
            return False
        return plex_running and transcoder_running

    def minutes_to_seconds(self, minutes):
        """Converts minutes to seconds"""
        return minutes * 60

    def cancel_shutdown(self):
        """Cancels the shutdown, returns true if the shutdown was canceled successfully"""
        if not self.shutdown_enabled:
            return False

        try:
            subprocess.run(["shutdown", "-a"], check=True)
            print("Auto-shutdown aborted")
            self.shutdown_enabled = False
            return True
        except subprocess.CalledProcessError:
            print("Shutdown was not canceled because it was not activated")
            return False

    def activate_shutdown(self, time_in_minutes):
        """Activates the shutdown"""
        if self.shutdown_enabled:
            return

        toast("Plex Auto Shutdown", "Auto-shutdown initiated")
        print(
            "Auto-shutdown initiated, computer will shutdown in "
            + str(time_in_minutes)
            + " seconds"
        )
        try:
            shutdown_delay = int(self.minutes_to_seconds(time_in_minutes))
            subprocess.run(
                [
                    "shutdown",
                    "-s",
                    "-t",
                    str(shutdown_delay),
                    "-c",
                    " ",
                ],
                check=True,
            )
            self.shutdown_enabled = True
        except subprocess.CalledProcessError as e:
            print("Shutdown was not activated, error: ", e)

    def monitor_plex_and_shutdown(self):
        """Checks if there is any active Plex session and computer is idling, if so, activates the shutdown
        returns NO_ACTIVATION if no action was taken, ACTIVATED_SHUTDOWN if the shutdown was activated and CANCELED_SHUTDOWN if the shutdown was canceled
        """
        print("\nMonitoring...")
        print("======================")
        if not self.app:
            return NO_ACTIVATION
        if not self.app.get_shutdown_status():
            self.cancel_shutdown()
            return NO_ACTIVATION

        max_idle_seconds = self.minutes_to_seconds(self.app.get_max_computer_idle())
        not_idling = max_idle_seconds != 0 and get_idle_duration() < max_idle_seconds

        # Si el max idle es 0 no se tiene en cuenta -> No se cancela el shutdown a menos que haya session nueva -> Tampoco se cuenta para activar el shutdown
        # Si el max idle es diferente de 0 entonces idle time tiene que ser menor al max -> Se cancela shutdown si el idle es menor al max o hay sesiones
        if self.shutdown_enabled:
            if not_idling or self.check_if_are_active_sessions():
                self.cancel_shutdown()
                return CANCELED_SHUTDOWN
            return NO_ACTIVATION

        if not_idling:
            print("Computer is not in idle mode")
            return NO_ACTIVATION
        print("Computer is in idle mode")

        if self.check_if_transcoder_running():
            print("Plex transcoder is running")
            return NO_ACTIVATION
        print("Plex transcoder is not running")

        if self.check_if_are_active_sessions():
            print("There are an active plex session")
            return NO_ACTIVATION
        print("No plex session is active")

        if not self.shutdown_enabled:
            self.activate_shutdown(self.app.get_shutdown_delay())
            return ACTIVATED_SHUTDOWN

        return NO_ACTIVATION

    def monitor_mainloop(self):
        """Main loop for the monitor thread"""
        if not self.app:
            return

        osSleep = WindowsInhibitor()
        osSleep.inhibit()
        while True:
            self.monitor_plex_and_shutdown()
            sleep(self.minutes_to_seconds(self.app.get_interval_delay()))
        osSleep.uninhibit()
