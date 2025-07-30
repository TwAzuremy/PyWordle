import config.config as config

from utils.utils import *
from .terminal_controller import TerminalController
from .key_handler import KeyHandler
from colorama import Fore
from blessed import Terminal
from typing import Dict

term = Terminal()


class UI:
    __tc = TerminalController()
    __columns, __lines = get_terminal_size()

    __banner = []
    __scrollable = False

    hotkey_tip = ''

    # The height at which the content is displayed.
    __game_display_contents_height = 0
    # The start render line of the information.
    __game_information_start_line = 0
    # The start render line of the shortcut text.
    __game_shortcut_start_line = 0
    # The start render line of the input box.
    __game_input_start_line = 0

    # Contents shown.
    __display_contents = []
    # The starting point taken from the displayed content.
    __intercept_point = 0
    # Content taken from the displayed content.
    __intercept_contents = []

    def __init__(self) -> None:
        self.__calc_game_size()

    def set_banner(self, file_path: str) -> None:
        with open(file_path, "r") as file:
            self.__banner = file.read().splitlines()

    @staticmethod
    def clear_screen() -> None:
        clear_screen()

    def render_cover(self, menu: list, gap: int = 1) -> int:
        clear_screen()

        # The structure is as follows:
        # ┌────────────────────────┐
        # │         banner         │
        # └────────────────────────┘
        # [space]
        # hotkey tip
        # [space]
        # ┌────────────────────────┐
        # │        options         │ Menu length Number of intervals.
        # └────────────────────────┘
        banner_offset = (2 + len(menu) + (len(menu) - 1) * gap) // 2
        after_banner_end_line = self.render_center_xy(self.__banner, 0, banner_offset * -1, True, False)

        # Locate the 'hotkey tip' line based on the end line.
        self.render_center_x(self.hotkey_tip, after_banner_end_line + 1, 0, False)
        self.__tc.flush()

        options_start_line = after_banner_end_line + 3
        options = [item['name'] for item in menu]

        on_enter = lambda index: (self.__tc.write_lines(options_start_line,
                                                        self.__build_options(options, gap, index),
                                                        options_start_line + len(menu) + (len(menu) - 1) * gap)
                                  .flush())

        return KeyHandler.register_menu(term, options, 0, on_enter)

    def render_menu(self, menu: list, gap: int = 1, selected: int = 0) -> int:
        clear_screen()

        options = [item['name'] for item in menu]
        start_line = self.render_center_xy(options, 0, gap * -1, False, False)

        on_enter = lambda index: (self.__tc.write_lines(start_line,
                                                        self.__build_options(options, gap, index),
                                                        start_line + len(menu) + (len(menu) - 1) * gap)
                                  .flush())

        return KeyHandler.register_menu(term, options, selected, on_enter)

    def __build_options(self, options: list[str], gap: int = 0, selected: int = 0) -> list[str]:
        buffer = []
        total_options = len(options)

        for i, option in enumerate(options):
            prefix = f"> " if i == selected else ""
            line = prefix + option

            fill_space = (self.__columns - visible_length(line) - len(prefix)) // 2

            centered_line = (Fore.GREEN if i == selected else "") + (" " * fill_space + line) + Fore.RESET
            buffer.append(centered_line)

            if i < total_options - 1:
                buffer.extend([""] * gap)

        return buffer

    def render_center_xy(self, content: list[str], offset_x: int = 0, offset_y: int = 0, render: bool = True,
                         flush: bool = True) -> int:
        start_line = (self.__lines - len(content)) // 2 + offset_y

        max_length = max((visible_length(line) for line in content), default=0)
        fill_space = (self.__columns - max_length) // 2 + offset_x

        if render:
            self.__tc.write_lines(start_line, [" " * fill_space + line for line in content], start_line + len(content))

        if flush:
            self.__tc.flush()

        return start_line + len(content)

    def render_center_x(self, string: str, line: int, offset_x: int = 0, flush: bool = True) -> None:
        fill = (self.__columns - visible_length(string)) // 2

        self.__tc.write_at(line, offset_x, " " * fill + string)
        if flush:
            self.__tc.flush()

    def render_center_y(self, content: list[str], offset_y: int = 0, flush: bool = True) -> None:
        start_line = ((self.__lines - len(content)) // 2) + offset_y

        self.__tc.write_lines(start_line, content, start_line + len(content))
        if flush:
            self.__tc.flush()

    def __calc_game_size(self) -> None:
        # UI general structure:
        # Title
        # ┌────────────────────────┐
        # │                        │ Display area ( 2 ~ n )
        # └────────────────────────┘
        # [space]
        # [INFO] Game information area ( n + 2 )
        # [space]
        # Shortcut key prompt area ( n + 4 )
        # ┌Input───────────────────┐
        # │                        │ Input area ( n + 5 ~ n + 7 )
        # └────────────────────────┘
        #
        # Subtract the fixed lines, and there are 8 lines in total (Contains empty rows).
        # The rest is the display area.
        self.__game_title = 1
        self.__game_display_contents_height = self.__lines - 8
        self.__game_information_start_line = self.__game_display_contents_height + 3
        self.__game_shortcut_start_line = self.__game_display_contents_height + 5
        self.__game_input_start_line = self.__game_display_contents_height + 6

    def input(self, title: str, input_tip: str, shortcut_tip: str, hotkey_list: list[Dict[str, any]] | None,
              exit_on_esc: bool = False) -> str:
        def on_render(text: str, disable: bool):
            self.__render_shortcut(input_tip, flush=False)
            self.__render_input(title, text, disable, flush=False)
            self.__tc.flush()

        def on_esc():
            self.set_shortcut(shortcut_tip)

            if hotkey_list is not None:
                return KeyHandler.register_hotkey(term, hotkey_list, lambda key: key == "e")()

            return None

        return KeyHandler.register_input(term, "", on_render, on_esc, exit_on_esc)

    @staticmethod
    def __build_input_structure(columns: int, title: str, text: str, disable: bool = False) -> list:
        """
        Construct a visual representation of an input box as a list of strings.

        The input box is represented using box-drawing characters, with an optional
        title and text content. The box can be styled differently based on the
        'disable' flag, which alters the color of the title line.

        The structure is as follows:
            ┌Input───────────────────┐
            │ |                      │
            └────────────────────────┘

        :param columns: The total width of the input box in characters.
        :type columns: int
        :param title: The title displayed at the top of the input box.
        :type title: str
        :param text: The text content displayed inside the input box.
        :type text: str
        :param disable: If True, the input box is styled as disabled.
        :type disable: bool

        :return: A list of strings, each representing a line in the input box structure.
        :rtype: list
        """
        top = f"{Fore.RESET if disable else Fore.YELLOW}┌{title}" + "─" * (columns - len(title) - 2) + "┐\n"
        middle = "│ " + text + " " * max(columns - visible_length(text) - 3, 0) + "│\n"
        bottom = "└" + "─" * (columns - 2) + f"┘{Fore.RESET}"

        return [top, middle, bottom]

    def __render_title(self, title: str, flush: bool = True):
        self.__tc.write_at(1, 0, title)

        if flush:
            self.__tc.flush()

    def __render_display(self, flush: bool = True):
        self.__tc.write_lines(2, self.__intercept_contents, self.__game_display_contents_height + 1)

        if flush:
            self.__tc.flush()

    @staticmethod
    def __build_row(arr: list[dict[str, str]]) -> list[str]:
        """
        Build and return the visual representation of a word as a list of strings.

        Each word is represented in a three-row format using box-drawing characters.
        The structure is as follows:
            ┌───┐\n
            │ A │\n
            └───┘

        :param arr: A list of dictionaries, where each dictionary represents a letter in the word.
                    The dictionary contains a single key-value pair, where the key is the letter itself,
        :type arr: list[dict[str, str]]

        :return: A list of strings, each representing a row in the three-row format.
        :rtype: list[str]
        """
        top_line, middle_line, bottom_lime = [], [], []

        for box in arr:
            if not box:
                letter = " "
                color = Fore.RESET
            else:
                letter, color = next(iter(box.items()))

            top_line.append(f"{color}┌───┐{Fore.RESET}")
            middle_line.append(f"{color}│ {letter} │{Fore.RESET}")
            bottom_lime.append(f"{color}└───┘{Fore.RESET}")

        return [
            ''.join(top_line),
            ''.join(middle_line),
            ''.join(bottom_lime)
        ]

    def __build_empty_table(self, length: int, line: int) -> list[str]:
        """
        Build and return the visual representation of an empty table as a list of strings.

        The structure is as follows:
            ┌───┐
            │   │
            └───┘

        :param length: The length of the words in the table.
        :type length: int
        :param line: The number of lines in the table.
        :type line: int

        :return: A list of strings, each representing a row in the table.
        :rtype: list[str]
        """
        empty_line = self.__build_row([{}] * length)

        return empty_line * line

    def __intercept_table(self, start: int, count: int):
        if count > len(self.__display_contents):
            count = len(self.__display_contents)

        self.__intercept_contents = self.__display_contents[start:start + count]

    def scroll_display_area(self, direction: str, step: int = 1) -> None:
        """
        Scrolls the display area either up or down by a given step, if scrolling is enabled.

        :param direction: The direction to scroll the display area.
        :type direction: str
        :param step: The number of lines to scroll by.
        :type step: int
        """
        # Check if scrolling is supported
        if not self.__scrollable:
            return

        # Scroll up or down based on the direction
        if direction == 'up':
            self.__intercept_point = max(0, self.__intercept_point - step)
        else:
            max_point = len(self.__display_contents) - self.__game_display_contents_height + 1
            self.__intercept_point = min(max_point, self.__intercept_point + step)

        # Update the intercept table and re-render the display
        self.__intercept_table(self.__intercept_point, len(self.__display_contents))
        self.__render_display()

    def __render_info(self, string: str, level: str = "info", flush: bool = True) -> None:
        """
        Renders a message with a specific log level, optionally flushing the output.

        The method handles different log levels by assigning specific colors to each one:
            - "info": Light black color.
            - "error": Red color.
            - "debug": Red color (if DEBUG mode is enabled).

        It also clears previous lines in the game info area before writing the new message.
        The log level prefix is displayed in uppercase to indicate the severity of the message.

        :param string: The message to display.
        :type string: str
        :param level: The log level that determines the message's importance and color.
        :type level: str
        :param flush: If True, flushes the output after rendering.
        :type flush: bool
        """
        # Define the mapping of log levels to colors
        color_map = {
            "info": Fore.LIGHTBLACK_EX,
            "error": Fore.RED,
            "debug": Fore.RED,
        }

        # Skip debug messages if DEBUG is not enabled
        if level == "debug" and not config.DEBUG:
            return

        # Get the color (default to RESET)
        color = color_map.get(level, Fore.RESET)
        prefix = f"[{level.upper()}]{Fore.RESET} "

        # Standardize the rendering logic
        self.__tc.clear_lines(self.__game_information_start_line)
        self.__tc.write_at(self.__game_information_start_line, 1, color + prefix + string)

        if flush:
            self.__tc.flush()

    def __render_shortcut(self, string: str, flush: bool = True) -> None:
        self.__tc.clear_lines(self.__game_shortcut_start_line)
        self.__tc.write_at(self.__game_shortcut_start_line, 1, string)

        if flush:
            self.__tc.flush()

    def __render_input(self, title: str, text: str, disable: bool = False, flush: bool = True) -> None:
        input_box = self.__build_input_structure(self.__columns, title, text, disable)

        (self.__tc
         .write_lines(self.__game_input_start_line, input_box, self.__game_input_start_line + len(input_box) - 1)
         .move_to(self.__game_input_start_line + 1, 3 + len(text)))

        if flush:
            self.__tc.flush()

    def render_game_structure(self, length: int, title: str, information: str, shortcut_tip: str) -> None:
        clear_screen()
        self.__intercept_point = 0

        self.__display_contents = render_line_numb(self.__build_empty_table(length, length + 1))
        self.__intercept_table(0, self.__game_display_contents_height)
        self.__scrollable = len(self.__display_contents) > self.__game_display_contents_height

        self.__render_title(title, flush=False)
        self.__render_display(flush=False)
        self.__render_info(information, flush=False)
        self.__render_shortcut(shortcut_tip, flush=False)
        self.__render_input("Input", "", flush=False)

        self.__tc.flush()

    def append(self, letter: list[dict[str, str]], line: int) -> None:
        """
        Appends a new row to the display area, calculates scroll distance if needed, and re-renders the display.

        This method performs the following steps:
        1. Calculates the index for the row based on the formula `3n - 2`, adjusting for 0-based indexing.
        2. Adds the new row with the appropriate line number and updates the display area.
        3. Calculates the display range (bounded by multiples of 3) and checks if the newly appended content fits within the current display area.
        4. If the content fits within the display range, it re-renders the display.
        5. If the content is outside the display range, it calculates the scroll distance based on the direction (up or down) and scrolls the display area accordingly.

        If the new row is within the current display range, it triggers a re-render of the display.
        If not, the display is scrolled either up or down to accommodate the new content.

        :param letter: The content to be appended, in the form of a list of dictionaries where each dictionary represents a row of data.
        :type letter: list[dict[str, str]]
        :param line: The line number indicating where the new row should be added.
        :type line: int
        """
        # Calculate the index for the line using the formula 3n - 2, adjusting for 0-based indexing
        list_line = 3 * line - 3

        # Add the line number and overwrite the original display_area
        self.__display_contents = overwrite_with_prefix(
            self.__display_contents,
            self.__build_row(letter),
            list_line
        )

        # Calculate the display range, where the boundaries are multiples of 3
        start = nearest_divisible_by_3(self.__intercept_point, "up")
        end = nearest_divisible_by_3(self.__intercept_point + self.__game_display_contents_height, "down")

        # Check if the newly appended content falls within the display range
        if start <= list_line < end:
            self.__intercept_table(self.__intercept_point, len(self.__display_contents))
            self.__render_display()
        else:
            # Calculate the scroll distance
            # up  : use the upper boundary and calculate the absolute difference
            # down: use the lower boundary and calculate the difference
            direction = 'up' if list_line <= self.__intercept_point else 'down'
            distance = (self.__intercept_point - list_line) if direction == 'up' \
                else (list_line + 3 - self.__intercept_point - self.__game_display_contents_height)
            self.scroll_display_area(direction, abs(distance))

    def set_information(self, information: str, level: str = "info"):
        self.__tc.clear_lines(self.__game_information_start_line)
        self.__render_info(information, level, flush=False)
        self.__tc.flush()

    def set_shortcut(self, shortcut_tip: str):
        self.__tc.clear_lines(self.__game_shortcut_start_line)
        self.__render_shortcut(shortcut_tip, flush=False)
        self.__tc.flush()
