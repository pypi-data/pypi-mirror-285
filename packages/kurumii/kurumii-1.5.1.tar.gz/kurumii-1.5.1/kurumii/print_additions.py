from datetime import datetime
def print_header(text):
    text = str(text)
    length = len(text)
    print("=" * length)
    print(text)
    print("=" * length)

def print_green(text):
    text = str(text)
    print("\033[92m" + text + "\033[0m")

def print_red(text):
    text = str(text)
    print("\033[91m" + text + "\033[0m")

def print_colored(text, hex_color):
    """
    Print the text in the specified color.
    
    :param text: The text to be printed.
    :param color: The color in which the text should be printed.
                  Options: 'green', 'red', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'black', 'gray', 
                           'lightgray', 'darkgray', 'lightblue', 'lightgreen', 'lightcyan', 'lightred', 'pink'
                  Optionally, the color can be specified as a hexadecimal string.
                  Optional: False
    """
    text = str(text)
    color_codes = {
        "green": "0;255;0",
        "red": "255;0;0",
        "yellow": "255;255;0",
        "blue": "0;0;255",
        "magenta": "255;0;255",
        "cyan": "0;255;255",
        "white": "255;255;255",
        "black": "0;0;0",
        "gray": "128;128;128",
        "lightgray": "211;211;211",
        "darkgray": "169;169;169",
        "lightblue": "173;216;230",
        "lightgreen": "144;238;144",
        "lightcyan": "224;255;255",
        "lightred": "255;182;193",
        "pink": "255;192;203",
    }

    if hex_color.lower() in color_codes:
        color = color_codes[hex_color.lower()]
    else:
        try:
            if hex_color[0] == "#":
                hex_color = hex_color[1:]
            if len(hex_color) != 6:
                raise ValueError("Hex color must be 6 characters long.")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            color = f"{r};{g};{b}"
        except ValueError as e:
            print(f"Error: {e}")
            return

    print(f"\033[38;2;{color}m{text}\033[0m")

def print_bold(text):
    """
    Print the text in bold.
    """
    text = str(text)
    print("\033[1m" + text + "\033[0m")

def print_underline(text):
    """
    Print the text in underlined.
    """
    text = str(text)
    print("\033[4m" + text + "\033[0m")

def print_italic(text):
    """
    Print the text in italic.
    """
    text = str(text)
    print("\033[3m" + text + "\033[0m")

def print_strikethrough(text):
    """
    Print the text in strikethrough.
    """
    text = str(text)
    print("\033[9m" + text + "\033[0m")

def print_danger(text):
    """
    Print the text in red and underlined.
    """
    text = str(text)
    print("\033[1;31;4m" + text + "\033[0m")

def print_warning(text):
    """
    Print the text in yellow and underlined.
    """
    text = str(text)
    print("\033[1;33;4m" + text + "\033[0m")

def print_success(text):
    """
    Print the text in green and underlined.
    """
    text = str(text)
    print("\033[1;32;4m" + text + "\033[0m")

def print_info(text):
    """
    Print the text in blue and underlined.
    """
    text = str(text)
    print("\033[1;34;4m" + text + "\033[0m")
def print_debug(text):
    """
    Print the text in cyan and underlined.
    """
    text = str(text)
    print("\033[1;36;4m" + text + "\033[0m")

def nice_print(text):
    '''
    print the text in green and with a timestamp.
    '''
    text = str(text)
    print(f"\033[1;32;4m[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: {text}\033[0m")

def print_system(text):
    '''
    print the text in underlined purple.
    '''
    text = str(text)
    print(f"\033[4;35;1mSystem:\033[0m {text}")