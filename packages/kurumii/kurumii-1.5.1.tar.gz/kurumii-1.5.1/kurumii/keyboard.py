import msvcrt
import time
import string

# Dictionary mapping special keys to their virtual key codes
SPECIAL_KEYS = {
    "enter": b'\r',
    "esc": b'\x1b',
    "del": b'\x7f',  # Delete key
    "backspace": b'\x08',
    "tab": b'\t',
    "space": b' ',
    "left": b'\xe0K',
    "right": b'\xe0M',
    "up": b'\xe0H',
    "down": b'\xe0P',
    "insert": b'\xe0R',
    "f1": b'\x80',
    "f2": b'\x81',
    "f3": b'\x82',
    "f4": b'\x83',
    "f5": b'\x84',
    "f6": b'\x85',
    "f7": b'\x86',
    "f8": b'\x87',
    "f9": b'\x88',
    "f10": b'\x89',
    "f11": b'\x8a',
    "f12": b'\x8b'
}
REVERSED_SPECIAL_KEYS = {v: k for k, v in SPECIAL_KEYS.items()}


def is_key_pressed(key):
    """
    Checks if a specific key is pressed.

    Args:
        - key (str): The key that should be checked for (case sensitive).
                
    Possibilities:
        - Alphabet (a-z)
        - Numbers (0-9)
        - Special keys: 
            - Enter
            - Space
            - Tab
            - Backspace
            - Escape
            - Arrow keys: Up, Down, Left, Right
            - Function keys: F1 to F12

    Returns:
        - bool: True if the key is pressed, False otherwise.
    """
    key = key.lower()
    key_pressed = False  # Flag to track key press

    # Check if the key is a special key
    if key in SPECIAL_KEYS:
        # Read the virtual key code for the special key
        virtual_key = SPECIAL_KEYS[key]
        key_pressed = msvcrt.kbhit() and msvcrt.getch() == virtual_key
    elif len(key) == 1 and key in string.ascii_letters + string.digits + string.punctuation:
        # Check if the key is a regular printable character
        key_pressed = msvcrt.kbhit() and msvcrt.getch().decode('utf-8') == key

    # Wait until the key is released
    while msvcrt.kbhit():
        msvcrt.getch()

    return key_pressed or False

def wait_for_keypress(key):
    """
    Pauses the execution until a specific key is pressed.

    Args:
        - key (str): The key to wait for (case sensitive).

    Possibilities:
        - Alphabet (a-z)
        - Numbers (0-9)
        - Special keys: 
            - Enter
            - Space
            - Tab
            - Backspace
            - Escape
            - Arrow keys: Up, Down, Left, Right
            - Function keys: F1 to F12
                
    Returns:
        - True: True if the specified key is pressed.
    """
    key = key.lower()
    while True:
        if key in SPECIAL_KEYS:
            if msvcrt.kbhit() and msvcrt.getch() == SPECIAL_KEYS[key]:
                return True
        elif len(key) == 1 and key in string.ascii_letters + string.digits + string.punctuation:
            if msvcrt.kbhit() and msvcrt.getch().decode('utf-8') == key:
                return True
        time.sleep(0.05)

def get_pressed_keys_list(termination_key="esc"):
    """
    Returns the keys that have been pressed until a termination key is pressed.

    Args:
        - termination_key (str): The key that terminates the function. Defaults to "esc".

    Possibilities:
        - Alphabet (a-z)
        - Numbers (0-9)
        - Special keys: 
            - Enter
            - Space
            - Tab
            - Backspace
            - Escape
            - Arrow keys: Up, Down, Left, Right
            - Function keys: F1 to F12

    Returns:
        - list: A list containing the keys that have been pressed.
    """
    pressed_keys = []
    termination_key = termination_key.lower()

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == SPECIAL_KEYS[termination_key]:
                break
            elif key in SPECIAL_KEYS.values():
                for k, v in SPECIAL_KEYS.items():
                    if v == key:
                        pressed_keys.append(k)
            elif key.decode('utf-8') in string.ascii_letters + string.digits + string.punctuation:
                pressed_keys.append(key.decode('utf-8'))
        time.sleep(0.05)

    return pressed_keys


def get_keypress():
    """
    Pauses the execution until a key is pressed, then returns the name of that key.

    Returns:
        - str: The name of the key pressed.
    """
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in SPECIAL_KEYS:
                return SPECIAL_KEYS[key]
            elif key in REVERSED_SPECIAL_KEYS:
                return REVERSED_SPECIAL_KEYS[key]
            else:
                decoded_key = key.decode('utf-8')
                if decoded_key in string.ascii_letters + string.digits + string.punctuation:
                    return decoded_key
                
import msvcrt

def wait_for_any_keypress():
    """
    Pauses the execution until any key is pressed, then returns True.

    - Returns:
        - True
    """
    msvcrt.getch()
    return True

def wait_for_either_keypress(keys):
    """
    Waits for either of the specified keys to be pressed.

    Args:
        - keys (list): List of keys to wait for.

    Returns:
        - True if either of the specified keys is pressed.
    """
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode()
            if key in keys:
                return True