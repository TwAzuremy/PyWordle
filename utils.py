import os

from blessed import Terminal

term = Terminal()


def clear_console():
    """
    Clears the console.

    This function calls either the 'cls' command if running on Windows or the
    'clear' command if running on a Unix system. This is used to clear the
    console screen.

    Returns:
        None
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
