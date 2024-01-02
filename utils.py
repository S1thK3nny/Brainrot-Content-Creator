import os
import inspect

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

def save_text(dir, things_to_say):
    try:
        with open(dir + "/text.txt", 'w') as file:
            for i in range(len(things_to_say)):
                if i == 0:
                    file.write(things_to_say[i])
                    file.write('\n')
                else:
                    for j in range(len(things_to_say[i])):
                        file.write("\n" + things_to_say[i][j])
                        file.write('\n')
    except Exception as e:
        sprint(f"Error writing to file: {e}")
