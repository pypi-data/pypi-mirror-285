from .utils.ui_controler import *
import warnings



def main():
    
    warnings.filterwarnings("ignore")

    end_program = False

    while not end_program:
        introduction_screen()
        print_current_page('menu')
        end_program = menu_screen()





