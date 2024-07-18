import sqlite3
import pandas as pd
import os
import types
from datetime import datetime

# from utils.sql_command import *

from .package_directory_manager import get_database_path, create_database_dir
from .sql_command import *
from .ANSI_color import *

'''
Database:

venv_info(id, project_path, venv_name, created_date, requirement_file, connect_status)

'''

def check_database():
    # If the database directory don't exist this function will create one, else pass
    create_database_dir()
    con = sqlite3.connect(get_database_path())
    cur = con.cursor()

    # If the require tables are not created, these functions will create them
    cur.execute(create_venv_info_sql)
    cur.execute(create_venv_log_sql)
    cur.execute(create_venv_insert_trigger_log_sql)
    cur.execute(create_venv_update_status_trigger_log_sql)
    con.close()

# It is RECOMMENDED to use this function to safely connect to the database
def connect_check_database():
    # This will return the connection to the database but it will check if the database is availabe first

    check_database()
    con = sqlite3.connect(get_database_path())
    return con

def insert_data_into_venv_info(*args, **kwargs):
    con = connect_check_database()
    cur = con.cursor()
    cur.execute(insert_into_venv_info_sql, (kwargs['project_path'], kwargs['venv_name'], kwargs['created_date'], kwargs['requirement_file'], kwargs['connect_status'], kwargs['last_modified']))
    con.commit()

def update_data_venv_info(*args, **kwargs):
    con = connect_check_database()
    cur = con.cursor()
    cur.execute(update_connect_status_venv_info_sql, (kwargs['connect_status'], kwargs['last_modified'], kwargs['venv_id']))
    con.commit()


def check_venv_connection(system_control: types.ModuleType, *args, **kwargs):
    con = connect_check_database()
    cur = con.cursor() 
    result = cur.execute(select_all_venv_view)
    venv_info = result.fetchall()
    for i in range(len(venv_info)):
        venv_id, venv_name, _, connect_status, project_path, _ = venv_info[i]
        # code_status = system_control.activate_venv(project_path, venv_name)
        # if code_status != 0 and connect_status != get_color_str('no', 'RED'):
        #     update_data_venv_info(con, connect_status = get_color_str('no', 'RED'), venv_name = venv_name, last_modified = datetime.now())
        if not system_control.check_venv(project_path, venv_name) and connect_status != get_color_str('no', 'RED'):
            update_data_venv_info(con, connect_status = get_color_str('no', 'RED'), venv_id = venv_id, last_modified = datetime.now())
    con.close()

