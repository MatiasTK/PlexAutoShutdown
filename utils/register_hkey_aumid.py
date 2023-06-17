import argparse
import pathlib

# noinspection PyCompatibility
import winreg
from typing import Optional


def register_hkey(appId: str, appName: str, iconPath: Optional[pathlib.Path]):
    if iconPath is not None:  # pragma: no cover
        if not iconPath.exists():
            raise ValueError(
                f"Could not register the application: File {iconPath} does not exist"
            )
        elif iconPath.suffix != ".ico":
            raise ValueError(
                f"Could not register the application: File {iconPath} must be of type .ico"
            )

    winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as masterKey:
        winreg.SetValueEx(masterKey, "DisplayName", 0, winreg.REG_SZ, appName)
        if iconPath is not None:  # pragma: no cover
            winreg.SetValueEx(
                masterKey, "IconUri", 0, winreg.REG_SZ, str(iconPath.resolve())
            )


def main():  # pragma: no cover
    app_id = "WinPlexAutoShutdown"
    app_name = "Windows Plex Auto Shutdown"
    app_icon = pathlib.Path("./icons/icon.ico")

    register_hkey(app_id, app_name, app_icon)
    print(f"Successfully registered the application ID '{app_id}'")


if __name__ == "__main__":
    main()
