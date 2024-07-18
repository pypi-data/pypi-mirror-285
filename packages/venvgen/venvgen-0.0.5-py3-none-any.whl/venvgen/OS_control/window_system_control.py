import os
import subprocess
# from commands.window_command import *
from ..commands.window_command import *


def get_os_name():
    return 'Windows'

def clear_screen():
    return_status = os.system(clear_screen_command)

def create_venv(project_directory, project_name):
    # subprocess.run([
    #     'cd', project_directory, '&&', 
    #     'python', '-m', 'venv', project_name
    #     ], shell = True)
    subprocess.run([
    'python', '-m', 'venv', f'{project_directory}\\{project_name}'
    ], shell = True)


def install_libraries(project_directory, venv, libraries):
    # os.system(f'cd "{project_directory}"\n' + venv + '\\Scripts\\activate.bat\npip install ' + libraries)
    subprocess.run([
        'cd', project_directory, '&&', 
        f'{venv}\\Scripts\\activate.bat', '&&', 
        'pip', 'install'
        ] + libraries, shell = True)
    
def install_libraries_with_requirement(project_directory, venv, requirement_file):
    subprocess.run([
        'cd', project_directory, '&&',
        f'{venv}\\Scripts\\activate.bat', '&&',
        'pip', 'install', '-r', f'{requirement_file}'
        ], shell = True)


def activate_venv(project_directory, venv):
    return os.system(f'cd "{project_directory}"\n' + venv + '\\Scripts\\activate.bat\n')

def install_system_library(library):
    subprocess.run(['pip', 'install', library], shell = True)

def check_venv(project_directory, venv):
    return os.path.exists(f'{project_directory}\\{venv}\\Scripts\\activate.bat')