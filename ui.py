from colorama import *
from utils import clear_console

import config


class UI:
    words = []
    length = 0
    number = 0

    information = ""
    other_msg = ""
    debug = ""

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

    @staticmethod
    def input(placeholder: str):
        return input(placeholder)

    def render(self):
        """
        Renders the current state of the game.

        This function displays the current state of the game by calling
        `__build_table` and printing the information and other messages.
        If the `DEBUG` flag is set to `True`, it also prints the debug message.
        """
        clear_console()

        self.__build_table()

        # Print information
        print(f"\n{Fore.CYAN}[INFO]{Fore.RESET} {self.information}")
        print(self.other_msg)

        if config.DEBUG:
            print(f"{Fore.RED}[DEBUG]{Fore.RESET} {self.debug}")
        else:
            print()

    def set_information(self, msg: str):
        self.information = msg

    def set_other_msg(self, msg: str):
        self.other_msg = msg

    def set_debug(self, msg: str):
        self.debug = msg

    def __build_table(self):
        empty_words = [[{" ": Fore.RESET} for _ in range(self.length)]
                       for _ in range(self.number - len(self.words))]

        print()
        for word in self.words + empty_words:
            rows = self.__build_rows(word)
            for row in rows:
                print(row)

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
