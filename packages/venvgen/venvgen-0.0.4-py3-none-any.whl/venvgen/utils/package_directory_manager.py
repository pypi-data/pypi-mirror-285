import os

def get_parent_directory(dir, level = 1):
    return os.path.dirname(dir)

def create_database_dir():
    database_dir = os.path.join(get_parent_directory(get_package_path()), 'database')

    if not os.path.exists(database_dir):
        os.makedirs(database_dir)

def get_package_path():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    return package_dir

def get_database_dir():
    return os.path.join(get_parent_directory(get_package_path()), 'database')

def get_database_path():
    return os.path.join(get_database_dir(), "venv_database.db")