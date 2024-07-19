import os
import subprocess
import ipywidgets
from IPython.display import display, SVG, Image

def do_nothing(one_argument): 
    return(one_argument)

dropbox_path = os.environ.get('DROPBOX_PATH')
def change_directory(path_string_windows_or_unix):
    os.chdir(fix_dropbox_location(path_string_windows_or_unix))

def translate_path(path_string_windows_or_unix):
    # For Mac, the OS is 'posix'.  For PC, the OS is "nt"
    directory_string = path_string_windows_or_unix.encode('unicode-escape').decode()
    if os.name == 'posix':
        directory_string = os.path.normpath(directory_string.replace(r'\\', '/'))
    return os.path.normpath(directory_string)

def fix_dropbox_location(path_string):
    # Adjust this function to use the 'dropbox_path' variable directly
    if dropbox_path and path_string.startswith("Dropbox"):
        p = path_string.replace("\\", "/")
        p = p.lower().replace("dropbox", "dropbox")  # This seems redundant as 'p' is already made lower case.
        p = p[p.find("dropbox"):]
        p = p[p.find("/"):]
        return translate_path(dropbox_path + p)
    else:
        return translate_path(path_string)

def double_click(path_or_file_string):
    # Resolve the full path before attempting to open
    full_path = fix_dropbox_location(path_or_file_string)

    try:
        if os.name == 'nt':  # Windows
            os.startfile(full_path)
        elif os.name == 'posix':  # Unix-like
            if 'darwin' in os.sys.platform:  # macOS
                subprocess.run(['open', full_path], check=True)
            else:  # Linux and others
                subprocess.run(['xdg-open', full_path], check=True)
    except Exception as e:
        print(f"Error opening file: {e}")

def double_click_button(file_name):
    # Resolve the full path before creating the button
    full_path = fix_dropbox_location(file_name)

    button = ipywidgets.Button(description=file_name, tooltip='Launch ' + file_name)
    display(button)

    def button_eventhandler(obj):
        # Use the resolved full path when the button is clicked
        double_click(full_path)
    
    button.on_click(button_eventhandler)

def display_graphic_file(file_name_with_path):
    if file_name_with_path.lower().endswith('.svg'):
        try:
            display(SVG(filename=file_name_with_path))
        except:
            print('SVG file is not displayable')
    else:
       try:
           display(Image(filename=file_name_with_path))
       except:
           print('graphic file is not displayable')