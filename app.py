""" This file contains the main GUI class and its function """
from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING

import customtkinter
import pystray
from PIL import Image
from plexapi.server import PlexServer
from pystray import MenuItem as item
from win11toast import toast

from config import (
    write_config,
    default_computer_idle,
    default_interval_delay,
    default_plex_token,
    default_plex_url,
    default_shutdown_delay,
)

customtkinter.set_appearance_mode("dark")

if TYPE_CHECKING:
    from plex_shutdown_manager import PlexShutdownManager


class App(customtkinter.CTk):
    """Main GUI class"""

    plex: PlexServer = None
    plex_shutdown_manager: PlexShutdownManager = None
    shutdown_switch_enabled = False
    shutdown_switch_on_show_end_enabled = False
    plex_url = default_plex_url
    plex_token = default_plex_token
    shutdown_delay = default_shutdown_delay
    interval_delay = default_interval_delay
    computer_idle = default_computer_idle

    def __init__(
        self,
        plex_url,
        plex_token,
        computer_idle,
        interval_delay,
        shutdown_delay,
        plex_shutdown_manager,
    ):
        super().__init__(fg_color="#2b2b2b")
        if plex_token != default_plex_token:
            try:
                self.plex = PlexServer(plex_url, plex_token)
            except ConnectionError:
                self.show_error("Connection error")
            except:
                self.show_error("Unknown error, maybe you are using an unvalid token")

        self.plex_url = plex_url
        self.plex_token = plex_token
        self.computer_idle = computer_idle
        self.interval_delay = interval_delay
        self.shutdown_delay = shutdown_delay
        self.computer_idle = computer_idle
        self.plex_shutdown_manager = plex_shutdown_manager

        self.title("Plex Auto Shutdown")
        self.resizable(False, False)
        self.iconbitmap("./icons/app.ico")

        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        # Auto Shutdown
        customtkinter.CTkButton(
            self,
            text="Toggle Auto Shutdown",
            command=lambda: self.toggle_shutdown_switch(auto_shutdown_label),
        ).grid(row=0, column=0, padx=10, pady=(20, 10))
        auto_shutdown_label = customtkinter.CTkLabel(
            self,
            text=f"Auto Shutdown is currently: {'ON' if self.shutdown_switch_enabled else 'OFF'}",
        )
        auto_shutdown_label.grid(row=0, column=1, padx=10, pady=(20, 10))

        # Auto Shutdown on Show End
        customtkinter.CTkButton(
            self,
            text="Shutdown when show ends",
            command=lambda: self.show_error("Not implemented yet"),
        ).grid(row=1, column=0, padx=10, pady=10)
        customtkinter.CTkLabel(
            self,
            text=f"Shutdown when show ends is: {'ON' if self.shutdown_switch_on_show_end_enabled else 'OFF'}",
        ).grid(row=1, column=1, padx=10, pady=10)

        # Plex URL
        customtkinter.CTkLabel(self, text="Plex URL").grid(
            row=2, column=0, padx=10, pady=(10, 0)
        )
        plex_url_entry = customtkinter.CTkEntry(self)
        plex_url_entry.grid(row=3, column=0, padx=10, pady=(0, 10))
        plex_url_entry.insert(0, self.plex_url)

        # Plex Token
        customtkinter.CTkLabel(self, text="Plex Token").grid(
            row=2, column=1, padx=10, pady=(10, 0)
        )
        plex_token_entry = customtkinter.CTkEntry(self)
        plex_token_entry.grid(row=3, column=1, padx=10, pady=(0, 10))
        plex_token_entry.insert(0, self.plex_token)

        # Shutdown Delay
        customtkinter.CTkLabel(self, text="Shutdown after (minutes)").grid(
            row=4, column=0, padx=10, pady=(10, 0)
        )
        shutdown_delay_entry = customtkinter.CTkEntry(self)
        shutdown_delay_entry.grid(row=5, column=0, padx=10, pady=(0, 10))
        shutdown_delay_entry.insert(0, self.shutdown_delay)

        # Interval Delay
        customtkinter.CTkLabel(self, text="Check every (minutes)").grid(
            row=4, column=1, padx=10, pady=(10, 0)
        )
        interval_delay_entry = customtkinter.CTkEntry(self)
        interval_delay_entry.grid(row=5, column=1, padx=10, pady=(0, 10))
        interval_delay_entry.insert(0, self.interval_delay)

        # Idle Time
        customtkinter.CTkLabel(self, text="After Idle time (minutes)").grid(
            row=6, column=0, padx=10, pady=(10, 0)
        )
        max_idle_delay_entry = customtkinter.CTkEntry(self)
        max_idle_delay_entry.grid(row=7, column=0, padx=10, pady=(0, 10))
        max_idle_delay_entry.insert(0, self.computer_idle)

        # Reset Default Values
        customtkinter.CTkButton(
            self,
            text="Reset Default Values",
            command=lambda: self.reset_settings(
                plex_url_entry,
                plex_token_entry,
                shutdown_delay_entry,
                interval_delay_entry,
                max_idle_delay_entry,
            ),
        ).grid(row=7, column=1, padx=10, pady=10)

        # Apply Settings
        customtkinter.CTkButton(
            self,
            text="Apply Settings",
            command=lambda: self.apply_settings(
                plex_url_entry,
                plex_token_entry,
                shutdown_delay_entry,
                interval_delay_entry,
                max_idle_delay_entry,
            ),
        ).grid(row=8, column=0, columnspan=6, padx=10, pady=10)

        # Author
        author_label = customtkinter.CTkLabel(
            self,
            text="Made by MatiasTK",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        )
        author_label.bind(
            "<Button-1>", command=lambda e: self.open_url("https://github.com/MatiasTK")
        )
        author_label.grid(row=10, column=0, padx=10, pady=10)

        # How to get token label
        how_to_get_token_label = customtkinter.CTkLabel(
            self,
            text="How to get your Plex Token?",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        )
        how_to_get_token_label.bind(
            "<Button-1>",
            command=lambda e: self.open_url(
                "https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/"
            ),
        )
        how_to_get_token_label.grid(row=10, column=1, padx=10, pady=10)

    def hide_window(self):
        """Hides the window and shows the icon in the system tray"""
        self.withdraw()

        image = Image.open("./icons/plex.png")
        menu = (
            item("Show", self.show_window, default=True),
            item("Quit", self.quit_window),
        )
        icon = pystray.Icon("PlexAutoShutdown", image, "Plex Auto Shutdown", menu)
        toast(
            "Plex Auto Shutdown",
            "Plex auto shutdown is on the system tray",
        )
        icon.run()

    def quit_window(self, icon):
        """Ends the program"""
        icon.stop()
        self.quit()

    def show_window(self, icon):
        """Deiconifies the window"""
        self.deiconify()
        icon.stop()

    def toggle_shutdown_switch(self, label):
        """Toggles the auto shutdown switch, if it's enabled it will stop the auto shutdown"""
        self.shutdown_switch_enabled = not self.shutdown_switch_enabled
        if self.shutdown_switch_enabled:
            self.show_success("Auto Shutdown is now ON")
            label.configure(text="Auto Shutdown is currently: ON")
        else:
            self.plex_shutdown_manager.cancel_shutdown()
            self.show_success("Auto Shutdown Disabled")
            label.configure(text="Auto Shutdown is currently: OFF")

    def show_error(self, message):
        """Shows an error message for 5 seconds"""
        error_label = customtkinter.CTkLabel(
            self, text=f"Error: {message}", text_color="red", font=("Arial", 12, "bold")
        )
        error_label.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
        self.after(5000, error_label.destroy)

    def show_success(self, message):
        """Shows a success message for 5 seconds"""
        success_label = customtkinter.CTkLabel(
            self,
            text=f"Success: {message}",
            text_color="green",
            font=("Arial", 12, "bold"),
        )
        success_label.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
        self.after(5000, success_label.destroy)

    def apply_settings(
        self,
        url_entry,
        token_entry,
        shutdown_delay_entry,
        interval_delay_entry,
        max_idle_delay_entry,
    ):
        """Applies the settings to the program"""
        self.plex_token = token_entry.get()
        if self.plex_token == "Your Plex Token Here":
            self.show_error("You need to enter a valid Plex Token first")
            return
        self.plex_shutdown_manager.cancel_shutdown()
        self.shutdown_switch_enabled = False
        self.shutdown_switch_on_show_end_enabled = False
        self.plex_url = url_entry.get()
        self.computer_idle = float(max_idle_delay_entry.get())
        self.interval_delay = float(interval_delay_entry.get())
        self.shutdown_delay = float(shutdown_delay_entry.get())
        try:
            self.plex = PlexServer(self.plex_url, self.plex_token)
            write_config(
                self.plex_url,
                self.plex_token,
                self.computer_idle,
                self.interval_delay,
                self.shutdown_delay,
            )
            self.show_success("Settings applied")
        except ConnectionError:
            self.show_error("Connection error")
            return
        except:
            self.show_error("Unknown error, maybe you are using an unvalid token")
            return

    def reset_settings(
        self,
        url_entry,
        token_entry,
        shutdown_delay_entry,
        interval_delay_entry,
        max_idle_delay_entry,
    ):
        """Resets the settings to the default values"""
        self.plex_token = default_plex_token
        self.plex_url = default_plex_url
        self.computer_idle = default_computer_idle
        self.interval_delay = default_interval_delay
        self.shutdown_delay = default_shutdown_delay

        url_entry.delete(0, "end")
        url_entry.insert(0, self.plex_url)

        token_entry.delete(0, "end")
        token_entry.insert(0, self.plex_token)

        shutdown_delay_entry.delete(0, "end")
        shutdown_delay_entry.insert(0, self.shutdown_delay)

        interval_delay_entry.delete(0, "end")
        interval_delay_entry.insert(0, self.interval_delay)

        max_idle_delay_entry.delete(0, "end")
        max_idle_delay_entry.insert(0, self.computer_idle)

        write_config(
            self.plex_url,
            self.plex_token,
            self.computer_idle,
            self.interval_delay,
            self.shutdown_delay,
        )
        self.show_success("Settings reseted")

    def open_url(self, url):
        """Opens a web browser with the given url"""
        webbrowser.open(url)

    def get_shutdown_status(self):
        """Returns the status of the shutdown switch"""
        return self.shutdown_switch_enabled

    def get_computer_idle(self):
        """Returns the computer idle time in minutes"""
        return self.computer_idle

    def get_plex_instance(self):
        """Returns the plex server instance"""
        return self.plex

    def get_shutdown_delay(self):
        """Returns the shutdown delay in minutes"""
        return self.shutdown_delay

    def get_interval_delay(self):
        """Returns the interval delay in minutes"""
        return self.interval_delay
