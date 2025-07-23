import os
import sys


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


def rewrite_lines(start_line, end_line, contents):
    """
    Rewrite a range of lines on the console with new content.

    This function rewrites a range of lines on the console with new content. The
    content must be a list of strings with a length equal to the number of
    lines being rewritten. The function will raise a ValueError if the length
    of the content is not equal to the number of lines being rewritten.

    Args:
        start_line (int): The line number to start rewriting from.
        end_line (int): The line number to end rewriting at.
        contents (list[str]): The new content to write to the console.

    Returns:
        None
    """
    if len(contents) != (end_line - start_line + 1):
        raise ValueError("Contents length must be equal to the number of lines to rewrite")

    save_cursor_position()
    hide_cursor()

    for i, line_num in enumerate(range(start_line, end_line + 1)):
        sys.stdout.write(f"\033[{line_num};0H")
        sys.stdout.write("\033[2K")
        sys.stdout.write(contents[i])

        if line_num == end_line:
            sys.stdout.write("\n")

    restore_cursor_position()
    show_cursor()


def clear_current_line():
    hide_cursor()
    sys.stdout.write("\033[u\033[2K")
    show_cursor()


def save_cursor_position():
    sys.stdout.write("\033[s")
    sys.stdout.flush()


def restore_cursor_position():
    sys.stdout.write("\033[u")
    sys.stdout.flush()


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
