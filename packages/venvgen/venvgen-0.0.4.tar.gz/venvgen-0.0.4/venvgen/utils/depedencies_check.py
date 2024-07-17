from .check_os import check_os
from .ANSI_color import get_color_str, print_color

def check_dependencies():
    OS = check_os()

    try:
        import inquirer
    except ModuleNotFoundError as e:
        print()
        print(f'{get_color_str('inquirer', 'RED')} module have not yet installed')
        print()
        print('Do you want to download it to your machine?')
        print()
        print('The library is Required for the program to run')
        userChoice = input('Your choice (Y/n): ')
        if userChoice == 'Y' or userChoice == 'y':
            OS.install_system_library('inquirer')
            print()
            print('Please rerun the program after installation')
            exit()        
        else:
            print()
            print_color('Cannot process further due to the lack of library', 'RED')
            exit()

    try:
        import pandas
    except ModuleNotFoundError as e:
        print()
        print(f'{get_color_str('pandas', 'RED')} module have not yet installed')
        print()
        print('Do you want to download it to your machine?')
        print()
        print('The library is Required for the program to run')
        userChoice = input('Your choice (Y/n): ')
        if userChoice == 'Y' or userChoice == 'y':
            OS.install_system_library('pandas')
            print()
            print('Please rerun the program after installation')
            exit()        
        else:
            print()
            print_color('Cannot process further due to the lack of library', 'RED')
            exit()

    try:
        import tabulate
    except ModuleNotFoundError as e:
        print()
        print(f'{get_color_str('tabulate', 'RED')} module have not yet installed')
        print()
        print('Do you want to download it to your machine?')
        print()
        print('The library is Required for the program to run')
        userChoice = input('Your choice (Y/n): ')
        if userChoice == 'Y' or userChoice == 'y':
            OS.install_system_library('tabulate')
            print()
            print('Please rerun the program after installation')
            exit()        
        else:
            print()
            print_color('Cannot process further due to the lack of library', 'RED')
            exit()
