import os
# from commands.macos_command import *
from ..commands.macos_command import *

def get_os_name():
    return 'MacOS'

def clear_screen():
    return_status = os.system(clear_screen_command)

def create_venv(project_directory, project_name):
    os.system(f'cd "{project_directory}"\n' + CREATE_VENV + project_name)

def install_libraries(project_directory, venv, libraries):
    os.system(f'cd "{project_directory}"\n' + 'source ' + venv + '/bin/activate\npip install ' + libraries)

def install_libraries_with_requirement(project_directory, venv, requirement_file):
    os.system(f'cd "{project_directory}"\n' + 'source ' + venv + '/bin/activate\npip install -r ' + f'"{requirement_file}"')

def activate_venv(project_directory, venv):
    return os.system(f'cd "{project_directory}"\n' + 'source ' + venv + '/bin/activate\n')

def install_system_library(library):
    os.system(f'pip install {library}')

def check_venv(project_directory, venv):
    return os.path.exists(f'{project_directory}/{venv}/bin/activate')