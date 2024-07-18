import re

def str_to_list(text):
    pattern = r'\s'
    pattern = re.compile(pattern, re.X)
    no_white_space_str = re.sub(pattern, '', text)
    str_ls = no_white_space_str.split(',')
    return str_ls

def list_to_str(word_ls, sep = ' '):
    result = ''
    for word in word_ls:
        result = result + word + sep
    result.strip()
    return result


