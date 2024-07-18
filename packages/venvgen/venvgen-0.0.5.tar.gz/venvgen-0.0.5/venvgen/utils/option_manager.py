# from utils.system_control_protocol import *
# from utils.database_manager import *

from .system_control_protocol import *
from .database_manager import (
    connect_check_database, 
    insert_data_into_venv_info, 
    select_all_venv_view,
    select_top_latest_create_data_venv_view,
    select_top_latest_modified_data_venv_view,
    select_top_earliest_create_data_venv_view,
    select_top_earliest_modified_data_venv_view,
    select_specific_venv
)
from datetime import date, datetime
from .package_directory_manager import get_database_dir, get_database_path
from .ANSI_color import *
from .system_check import refresh_check
import pandas as pd

def option1(display_function, *args, **kwargs):
    refresh_check()
    print(get_database_dir())
    con = connect_check_database()

    first_time = True
    project_directory = None

    while first_time or (not first_time and (project_directory == None or project_directory == '')):
        project_directory = display_function(first_time, 'project_directory')
        first_time = False
    
        if project_directory == GO_BACK_TO_MENU_PAGE:
            return False
    
    first_time = True
    venv_name = None
    
    while first_time or (not first_time and (venv_name == None or venv_name == '')):
        venv_name = display_function(first_time, 'venv', project_directory = project_directory)
        first_time = False

        if venv_name == GO_BACK_TO_MENU_PAGE:
            return False
        
    first_time = True
    require_name = None

    while first_time or (not first_time and (require_name == None or require_name == '')):
        require_name = display_function(first_time, 'requirement', venv = venv_name, project_directory = project_directory)
        first_time = False

        if require_name == None:
            pass

        elif require_name == GO_BACK_TO_MENU_PAGE:
            return False
        
        elif require_name != NO_REQUIREMENTS_FILE:
            try:
                with open(require_name, 'r') as f:
                    f.readline()
            except FileNotFoundError as e:
                require_name = None
    
    if require_name == NO_REQUIREMENTS_FILE:
        first_time = True
        libraries = None

        while first_time or (not first_time and (libraries == None or libraries == '')):
            libraries = display_function(first_time, 'library_manual_input', venv = venv_name, project_directory = project_directory)
            first_time = False

            if libraries == GO_BACK_TO_MENU_PAGE:
                return False

        kwargs['system_control'].create_venv(project_directory, venv_name)
        insert_data_into_venv_info(con, project_path = project_directory, venv_name = venv_name, created_date = date.today(), requirement_file = None, connect_status = get_color_str('yes', 'GREEN'), last_modified = datetime.now())

        if libraries != NO_LIBRARIES:
            kwargs['system_control'].install_libraries(project_directory, venv_name, libraries)
        return False
    
    if require_name != NO_REQUIREMENTS_FILE:
        kwargs['system_control'].create_venv(project_directory, venv_name)
        kwargs['system_control'].install_libraries_with_requirement(project_directory, venv_name, require_name)
        insert_data_into_venv_info(con, project_path = project_directory, venv_name = venv_name, created_date = date.today(), requirement_file = require_name, connect_status = get_color_str('yes', 'GREEN'), last_modified = datetime.now())
        


    else:
        kwargs['system_control'].create_venv(project_directory, venv_name)
        insert_data_into_venv_info(con, project_path = project_directory, venv_name = venv_name, created_date = date.today(), requirement_file = None, connect_status = get_color_str('yes', 'GREEN'), last_modified = datetime.now())

    con.close()

def option2_1(display_function, con):
    refresh_check()
    all_venv_df = pd.read_sql(select_all_venv_view, con)
    display_function(first_time = True, step = 'display_all_venv', df = all_venv_df)
    return False
    
def option2_2_1(display_function, con):
    no_of_row = display_function(first_time = True, step = 'input_no_of_rows_latest_create')
    no_of_row_str = str(no_of_row)

    latest_create_venv_df = pd.read_sql(select_top_latest_create_data_venv_view.replace('?', no_of_row_str), con)
    display_function(first_time = True, step = 'display_latest_create_date', df = latest_create_venv_df)
    return False

def option2_2_2(display_function, con):
    no_of_row = display_function(first_time = True, step = 'input_no_of_rows_latest_modified')
    no_of_row_str = str(no_of_row)

    latest_modified_venv_df = pd.read_sql(select_top_latest_modified_data_venv_view.replace('?', no_of_row_str), con)
    display_function(first_time = True, step = 'display_latest_modified_time', df = latest_modified_venv_df)
    return False

def option2_2_3(display_function, con):
    no_of_row = display_function(first_time = True, step = 'input_no_of_rows_earliest_create')
    no_of_row_str = str(no_of_row)

    earliest_create_venv_df = pd.read_sql(select_top_earliest_create_data_venv_view.replace('?', no_of_row_str), con)
    display_function(first_time = True, step = 'display_earliest_create_date', df = earliest_create_venv_df)
    return False

def option2_2_4(display_function, con):
    no_of_row = display_function(first_time = True, step = 'input_no_of_rows_earliest_modified')
    no_of_row_str = str(no_of_row)

    earliest_modified_venv_df = pd.read_sql(select_top_earliest_modified_data_venv_view.replace('?', no_of_row_str), con)
    display_function(first_time = True, step = 'display_earliest_modified_time', df = earliest_modified_venv_df)
    return False

    
def option2_2(display_function, con):
    refresh_check()

    to_view_menu = False

    while not to_view_menu:
        user_choice = display_function(first_time = True, step = 'display_with_filter')

        if user_choice == '1':
            to_view_menu = option2_2_1(display_function, con)
        elif user_choice == '2':
            to_view_menu = option2_2_2(display_function, con)
        elif user_choice == '3':
            to_view_menu = option2_2_3(display_function, con)
        elif user_choice == '4':
            to_view_menu = option2_2_4(display_function, con)
        elif user_choice == '5':
            return False

    return False

def option2_3(display_function, con):
    venv_id = display_function(first_time = True, step = 'input_venv_id')
    if venv_id == GO_BACK_TO_VIEW_VENV:
        return False
    else:
        venv_detail = pd.read_sql(select_specific_venv.replace('?', str(venv_id)), con)
        display_function(first_time = True, step = 'display_specific_venv', df = venv_detail)


def option2(display_function, *args, **kwargs):
    refresh_check()
    con = connect_check_database()

    

    to_main_menu = False

    while not to_main_menu:
        user_choice = display_function(first_time = True, step = 'view_venv_menu')
        if user_choice == '5':
            return False
        

        elif user_choice == '1':

            to_main_menu = option2_1(display_function, con)
        

        elif user_choice == '2':
            to_main_menu = option2_2(display_function, con)
        

        elif user_choice == '3':
            to_main_menu = option2_3(display_function, con)
        
        elif user_choice == '4':
            return False







    pass