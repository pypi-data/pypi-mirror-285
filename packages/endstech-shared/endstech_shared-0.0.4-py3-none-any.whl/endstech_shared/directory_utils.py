import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths

PORTABLE_APP_DATA_DIR = "portable_data"


def is_portable(is_windows: bool, is_frozen: bool) -> bool:
    if not (is_windows and is_frozen):
        return False

    portable_data_dir = Path(sys.executable).parent / PORTABLE_APP_DATA_DIR

    return portable_data_dir.is_dir()


def get_app_data_dir(is_windows: bool, is_frozen: bool, is_dev: bool, module_directory: Path) -> Path:
    if is_portable(is_windows, is_frozen):
        return Path(sys.executable).parent / PORTABLE_APP_DATA_DIR

    if not is_dev:
        app_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    else:
        app_dir = module_directory.parent / PORTABLE_APP_DATA_DIR

    if not app_dir.is_dir():
        app_dir.mkdir(parents=True)

    return app_dir


def get_desktop_dir() -> Path:
    return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation))
