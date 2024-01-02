import os
import inspect
import string
import random

# Source Print - Not my best name, eh?
def sprint(message):
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    prefix = os.path.basename(filename)
    func = frame.f_code.co_name
    if func != '<module>':  # Exclude module-level
        prefix += ": " + func
    str = prefix + " - " + message
    print(str)
    return str

def write_to_info_file(dir, text):
    info_filename = f"{dir}/info.txt"
    with open(info_filename, 'a', encoding='utf-8') as info_file:
        info_file.write(strip_special_chars(text) + '\n')

# THIS IS IMPORTANT! Fixes base64 decode error. If an audio file won't save anyway, try it again.
def strip_special_chars(text: str) -> str:
    printable = set(string.printable)
    return ''.join(filter(lambda x: x in printable, text))

def choose_random_file(dir):
    files = sorted(os.listdir(dir))
    return str(dir + random.choice([file for file in files]))

def save_text(dir, things_to_say):
    try:
        with open(dir + "/text.txt", 'w') as file:
            for i in range(len(things_to_say)):
                if i == 0:
                    file.write(strip_special_chars(things_to_say[i]))
                    file.write('\n')
                else:
                    for j in range(len(things_to_say[i])):
                        file.write("\n" + strip_special_chars(things_to_say[i][j]))
                        file.write('\n')
    except Exception as e:
        sprint(f"Error writing to file: {e}")

def check_file_exists(file_path, file_type):
    if file_path == None or not os.path.isfile(file_path):
        sprint(f"{file_type} not found!")
        return False
    return True