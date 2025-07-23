from colorama import *


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

    def print(self):
        """
        Print the words to the console.
        This will print only the first 'number' words from the 'words' list.
        If there are fewer words, empty words will be added.
        """
        # Only process the first 'number' words from the list
        words_to_print = self.words[:self.number]

        # Add empty words until the number of words reaches 'number'
        if len(self.words) < self.number:
            words_to_print += self.__get_empty_words(self.number - len(self.words))

        # Print each word (each word in a separate line)
        print()
        for word in words_to_print:
            rows = self.__build_rows(word)
            for row in rows:
                print(row)

        print()

    @staticmethod
    def __build_rows(arr: list[dict[str, str]]):
        """
        Build and return the visual representation of a word as a list of strings.

        Each word is represented in a three-row format using box-drawing characters.
        The structure is as follows:
            ┌─┐
            │A│
            └─┘

        Args:
            arr (list[dict[str, str]]): A list of dictionaries, where each dictionary
            contains a character as the key and its corresponding color as the value.

        Returns:
            list[str]: A list of three strings, representing the top, middle, and bottom
            rows of the word's visual representation.
        """
        top = ''.join([list(item.values())[0] + "┌─┐" for item in arr])
        mid = ''.join([f"{list(item.values())[0]}│{list(item.keys())[0]}│" for item in arr])
        bottom = ''.join([list(item.values())[0] + "└─┘" for item in arr])

        return [top, mid, bottom]

    def __get_empty_words(self, count: int):
        """
        Create a specified number of empty words (boxes with default color).

        Args:
            count (int): The number of empty words to create.

        Returns:
            list: A list of empty words represented as lists of dictionaries with space as the value.
        """
        # Each empty word consists of 'self.length' empty box placeholders
        return [[{" ": Fore.RESET} for _ in range(self.length)] for _ in range(count)]
