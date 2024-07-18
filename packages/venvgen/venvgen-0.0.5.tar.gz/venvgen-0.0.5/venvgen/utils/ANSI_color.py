from typing import Literal

ANSI_color_dict = {
    'RED': '91',
    'GREEN': '32',
    'BLUE': '34',
    'YELLOW': '93',
    'MANGRETA': '95',
    'BRIGHT WHITE': '97',
    'WHITE': '37'
}

def get_color_str(text: str, color: Literal['RED', 'GREEN', 'BLUE', 'YELLOW', 'MANGRETA', 'BRIGHT WHITE', 'WHITE']) -> str:
    START = f'\33[{ANSI_color_dict[color]}m'
    END   = '\33[m'
    return START + text + END


def print_color(text: str, color: str) -> None:
    START = f'\33[{ANSI_color_dict[color]}m'
    END   = '\33[m'
    print(START + text + END, end = '')


