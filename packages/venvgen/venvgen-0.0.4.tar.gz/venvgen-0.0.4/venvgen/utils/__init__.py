from .depedencies_check import check_dependencies
check_dependencies()



print('Importing system check...', end = '                                             \r')
# from . import system_check

# system_check.init_check()

# OS = system_check.check_os()

from .system_check import init_check, check_os

# init_check()
OS = check_os()


# print('Importing system control...', end = '                                          \r')
# from . import all_system_control

# print('Importing ANSI color...', end = '                                              \r')
# from . import ANSI_color

# print('Importing ANSI line modification...', end = '                                  \r')
# from . import ANSI_line_modification

# print('Importing database manager...', end = '                                        \r')
# from . import database_manager

# print('Importing macos system control...', end = '                                    \r')
# from . import macos_system_control

# print('Importing option manager...', end = '                                          \r')
# from . import option_manager

# print('Importing package directory manager...', end = '                                   \r')
# from . import package_directory_manager

# print('Importing sql command...', end = '                                             \r')
# from . import sql_command

# print('Importing string_processing', end = '                                          \r')
# from . import string_processing

# print('Importing system control protocol...', end = '                                 \r')
# from . import system_control_protocol

print('Importing UI controler...', end = '                                            \r')
from . import ui_controler

# print('Importing Window system control', end = '                                      \r')
# from . import window_system_control

