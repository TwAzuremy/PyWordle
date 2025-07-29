import re
import os
import sys

from colorama import Fore
from ui.font_style import italic


def clear_screen() -> None:
    """
    Clears the terminal screen.

    This function simply runs either 'cls' (on Windows) or 'clear' (on Unix-like systems) using the
    os.system() call. It does not do any advanced error checking or handling.

    :rtype: None
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def visible_length(text: str) -> int:
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    return len(ansi_escape.sub('', text))


def hotkey_style(text: str) -> str:
    return Fore.CYAN + italic(text) + Fore.RESET


def get_terminal_size() -> tuple:
    """
    Return the size of the terminal window in characters as a tuple (columns, lines).

    If the terminal size can't be determined, use the default size of 80x25.

    :returns: A tuple of two integers representing the terminal size in characters.
    :rtype: tuple
    """
    try:
        columns, lines = os.get_terminal_size()
    except (AttributeError, OSError):
        # For the Unix-like and Windows-like alternatives,
        # both scenarios have not been tested for proper functioning for the time being.
        import fcntl, termios, struct
        try:
            if sys.platform != 'win32':

                data = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b'\x00' * 8)
                lines, columns = struct.unpack('hh', data)
            else:
                from ctypes import windll, create_string_buffer

                hstd = windll.kernel32.GetStdHandle(-11)
                csbi = create_string_buffer(22)

                if windll.kernel32.GetConsoleScreenBufferInfo(hstd, csbi):
                    _, _, _, _, _, left, top, right, bottom, _, _ = struct.unpack("hhhhHhhhhhh", csbi.raw)
                    columns = right - left + 1
                    lines = bottom - top + 1
                else:
                    raise OSError

        except (ImportError, OSError, struct.error):
            columns = int(os.environ.get('COLUMNS', 80))
            lines = int(os.environ.get('LINES', 25))

    return columns, lines


def render_line_numb(arr: list[str]) -> list[str]:
    """
    This function handles the list of strings and adds the line number in front of the index that matches formula 3n - 2,
    start with an index of 1. The line numbers are formatted as two digits wide.

    :param arr: The list of strings to process.
    :type arr: list[str]

    :return: A new list where every third element (starting from the second) has a line number
             prepended to it. Other elements remain unchanged, with a space padding where no
             line number is added.
    :rtype: list[str]
    """
    result = []
    count = 1

    for i, item in enumerate(arr):
        # Add line number every third element starting from the second
        if (i + 2) % 3 == 0:
            prefix_numb = f"{count:2d} "
            count += 1
        else:
            prefix_numb = " " * 3

        result.append(prefix_numb + item)

    return result



def overwrite_with_prefix(list_a, list_b, start_index) -> list[str]:
    """
    This function overwrites elements of list_a with elements from list_b starting from the specified
    start_index. It keeps the first 3 characters of each element in list_a and appends the corresponding
    element from list_b. If list_b is longer than the part of list_a being overwritten, the remaining
    elements of list_b are appended to the end of the result.

    :param list_a: The original list whose elements will be overwritten.
    :type list_a: list of str
    :param list_b: The list whose elements will replace parts of list_a.
    :type list_b: list of str
    :param start_index: The index in list_a from which the overwriting will begin.
    :type start_index: int

    :return: A new list with elements from list_b overwriting parts of list_a,
             preserving the first 3 characters of the elements in list_a.
    :rtype: list of str
    """
    # Create a copy of list_a to avoid modifying the original list
    result = list_a.copy()

    # Ensure start_index is within a valid range
    if start_index < 0:
        start_index = 0
    elif start_index > len(result):
        start_index = len(result)

    # Iterate through list_b to perform the overwrite operation
    for i in range(len(list_b)):
        idx = start_index + i

        if idx < len(result):
            # Retain the first 3 characters of the original element and overwrite with list_b's element
            # Handles cases where the string is shorter than 3 characters
            prefix = result[idx][:3]
            result[idx] = prefix + list_b[i]
        else:
            # If the index exceeds the length of list_a, append list_b's element
            result.append(list_b[i])

    return result


def nearest_divisible_by_3(a, direction) -> int:
    """
    This function returns the nearest number divisible by 3 based on the given direction.
    It either rounds up or rounds down to the nearest multiple of 3.

    :param a: The number to be rounded to the nearest multiple of 3.
    :type a: int
    :param direction: The direction to round to. Should be either 'up' (round up) or 'down' (round down).
    :type direction: str

    :return: The nearest number divisible by 3 based on the direction specified.
    :rtype: int
    """
    if a == 0:
        return 0

    v = a % 3

    if direction == "up":
        return a - v + 3
    else:
        return a - v

