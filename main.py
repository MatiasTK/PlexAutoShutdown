""" Main entry point for the application. """
import subprocess
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
    app = App(
        plex_url,
        plex_token,
        computer_idle,
        interval_delay,
        shutdown_delay,
    )
    shutdown_manager = PlexShutdownManager(app)
    background = Thread(
        target=shutdown_manager.monitor_mainloop,
        daemon=True,
    )
    app.after(1000, background.start)
    app.mainloop()

    try:
        subprocess.run(["shutdown", "-a"], check=True)
    except subprocess.CalledProcessError:
        print("Tear down failed to cancel shutdown")
