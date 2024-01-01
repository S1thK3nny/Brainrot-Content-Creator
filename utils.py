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