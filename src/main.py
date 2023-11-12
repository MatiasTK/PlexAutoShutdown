""" Main entry point for the application. """
from threading import Thread

from app import App
from config import load_config
from plex_shutdown_manager import PlexShutdownManager

if __name__ == "__main__":
    (
        plex_url,
        plex_token,
        computer_idle,
        interval_delay,
        shutdown_delay,
    ) = load_config()
    shutdown_manager = PlexShutdownManager()
    app = App(
        plex_url,
        plex_token,
        computer_idle,
        interval_delay,
        shutdown_delay,
        shutdown_manager,
    )
    background = Thread(
        target=shutdown_manager.monitor_mainloop,
        args=(app,),
        daemon=True,
    )
    app.after(1000, background.start)
    app.mainloop()
