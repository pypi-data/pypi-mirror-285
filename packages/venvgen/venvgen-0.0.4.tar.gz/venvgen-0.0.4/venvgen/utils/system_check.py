from .ANSI_color import get_color_str, print_color
from .database_manager import check_database, check_venv_connection
from ..venvgen_version import __version__
from .depedencies_check import check_os
# import platform
# from ..OS_control import macos_system_control as MacOS, window_system_control as Windows
from types import ModuleType
import os


# def check_os() -> ModuleType:
#     if platform.system() == 'Darwin':
#         from ..OS_control import macos_system_control as OS
#         return OS
#     elif platform.system() == 'win32' or platform.system() == 'Windows':
#         from ..OS_control import macos_system_control as OS
#         return OS

# def check_ui_library():
#     OS = check_os()

#     try:
#         import inquirer
#     except ModuleNotFoundError as e:
#         print()
#         print(f'{get_color_str('inquirer', 'RED')} module have not yet installed')
#         print()
#         print('Do you want to download it to your machine?')
#         print()
#         print('The library is Required for the program to run')
#         userChoice = input('Your choice (Y/n): ')
#         if userChoice == 'Y' or userChoice == 'y':
#             OS.install_system_library('inquirer')
#             print()
#             print('Please rerun the program after installation')
#             exit()        
#         else:
#             print()
#             print_color('Cannot process further due to the lack of library', 'RED')
#             exit()

#     try:
#         import pandas
#     except ModuleNotFoundError as e:
#         print()
#         print(f'{get_color_str('pandas', 'RED')} module have not yet installed')
#         print()
#         print('Do you want to download it to your machine?')
#         print()
#         print('The library is Required for the program to run')
#         userChoice = input('Your choice (Y/n): ')
#         if userChoice == 'Y' or userChoice == 'y':
#             OS.install_system_library('pandas')
#             print()
#             print('Please rerun the program after installation')
#             exit()        
#         else:
#             print()
#             print_color('Cannot process further due to the lack of library', 'RED')
#             exit()

#     try:
#         import tabulate
#     except ModuleNotFoundError as e:
#         print()
#         print(f'{get_color_str('tabulate', 'RED')} module have not yet installed')
#         print()
#         print('Do you want to download it to your machine?')
#         print()
#         print('The library is Required for the program to run')
#         userChoice = input('Your choice (Y/n): ')
#         if userChoice == 'Y' or userChoice == 'y':
#             OS.install_system_library('tabulate')
#             print()
#             print('Please rerun the program after installation')
#             exit()        
#         else:
#             print()
#             print_color('Cannot process further due to the lack of library', 'RED')
#             exit()

def init_check():
    check_database()

def refresh_check():
    check_venv_connection(check_os())

def get_this_project_version():
    return __version__

def check_dir_connectivity(dir):
    return os.path.exists(dir)