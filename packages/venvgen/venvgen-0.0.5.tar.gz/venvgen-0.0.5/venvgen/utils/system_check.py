from .ANSI_color import get_color_str, print_color
from .database_manager import check_database, check_venv_connection
from ..venvgen_version import __version__
from .depedencies_check import check_os
# import platform
# from ..OS_control import macos_system_control as MacOS, window_system_control as Windows
from types import ModuleType
import os


def init_check():
    check_database()

def refresh_check():
    check_venv_connection(check_os())

def get_this_project_version():
    return __version__

def check_dir_connectivity(dir):
    return os.path.exists(dir)