from colorama import *
from utils import clear_console, rewrite_lines

import config


class UI:
    words = []
    length = 0
    number = 0

    def set_word_length(self, length: int):
        """
        Set the word length and update the number of words.

        Args:
            length (int): The desired length of the words.

        This function sets the instance variable 'length' to the given value
        and updates 'number' to be one more than the specified length.
        """
        self.length = length
        self.number = length + 1

    def get_length(self):
        return self.length

    def get_number(self):
        return self.number

    def clear(self):
        """Clears the list of words, resetting it to an empty state."""
        self.words = []

    def insert(self, word: list[dict[str, str]]):
        """
        Inserts a word into the list of words if its length matches the set word length.

        Args:
            word (list[dict[str, str]]): A list of dictionaries representing the word,
            where each dictionary contains a character as the key and its corresponding
            color as the value.
        """
        if len(word) == self.length:
            self.words.append(word)
            self.__rewrite_table(len(self.words), word)

    def build_empty_table(self, info: str, other_msg: str):
        """
        Constructs and displays an empty table structure on the console.

        This function clears the console and generates a visual representation
        of an empty table based on the specified word length. Each "cell" of
        the table is represented by a box-drawing character. It also prints
        additional informational and other messages below the table.

        Args:
            info (str): The informational message to display after the table.
            other_msg (str): An additional message to display after the informational
                             message.
        """
        clear_console()
        empty_words = [[{" ": Fore.RESET} for _ in range(self.length)] for _ in range(self.number)]

        print()
        for word in empty_words:
            rows = self.__build_rows(word)
            for row in rows:
                print(row)

        print(f"\n{Fore.CYAN}[INFO]{Fore.RESET} " + info)
        print(f"{other_msg}")
        print(f"{Fore.RED}[DEBUG]{Fore.RESET} " + f"Debug mode is {config.DEBUG}")

    def print_info(self, info: str):
        """
        Prints an information message on a specific line on the console.

        The message is printed on the line below the debug message line.
        The line number is calculated based on the number of words in the table.

        Args:
            info (str): The message to be printed.
        """
        info_line = 3 + 3 * self.number

        rewrite_lines(info_line, info_line, [f"{Fore.CYAN}[INFO]{Fore.RESET} " + info])

    def print_other_msg(self, other_msg: str):
        """
        Prints a message on a specific line on the console.

        The message is printed on the line below the debug message line.
        The line number is calculated based on the number of words in the table.

        Args:
            other_msg (str): The message to be printed.
        """
        msg_line = 4 + 3 * self.number

        rewrite_lines(msg_line, msg_line, [other_msg])

    def print_debug(self, debug: str):
        """
        Print a debug message on the console if debug mode is enabled.

        The message is displayed in red and is formatted with a debug prefix.
        It is printed on a specific line depending on the current number of words.

        Args:
            debug (str): The debug message to be printed.
        """
        if config.DEBUG:
            debug_line = 5 + 3 * self.number

            rewrite_lines(debug_line, debug_line, [f"{Fore.RED}[DEBUG]{Fore.RESET} " + debug])

    @staticmethod
    def __build_rows(arr: list[dict[str, str]]):
        """
        Build and return the visual representation of a word as a list of strings.

        Each word is represented in a three-row format using box-drawing characters.
        The structure is as follows:
            ┌───┐
            │ A │
            └───┘

        Args:
            arr (list[dict[str, str]]): A list of dictionaries, where each dictionary
            contains a character as the key and its corresponding color as the value.

        Returns:
            list[str]: A list of three strings, representing the top, middle, and bottom
            rows of the word's visual representation.
        """
        top = ''.join([list(item.values())[0] + "┌───┐" for item in arr])
        mid = ''.join([f"{list(item.values())[0]}│ {list(item.keys())[0]} │" for item in arr])
        bottom = ''.join([list(item.values())[0] + "└───┘" for item in arr])

        return [top, mid, bottom]

    def __rewrite_table(self, row:int, content:list[dict[str, str]]):
        # Depending on the style of the output, three lines count as one line. So the beginning of a line is 3n - 2,
        # and since the first line is empty, you need to add 1.
        """
        Rewrite a table row at a given position with new content.

        The table structure is as follows:
            1. Empty line
            2. Top of the box
            3. Middle of the box
            4. Bottom of the box
            5. Empty line

        Args:
            row (int): The row number to rewrite, starting from 1.
            content (list[dict[str, str]]): The new content of the row, where each dictionary
            contains a character as the key and its corresponding color as the value.

        Returns:
            None
        """
        line = 3 * row - 1
        rewrite_lines(line, line + 2, self.__build_rows(content))
