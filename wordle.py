from colorama import *
from utils import *

import random


class Wordle:
    MIN_WORD_LENGTH = 3

    word_list = {}

    is_win = False
    current_word = ""
    opportunity = 0

    def __init__(self, file_path: str):
        self.__process_file(file_path)

        self.min_length = min(self.word_list.keys())
        self.max_length = max(self.word_list.keys())

    def __process_file(self, file_path: str):
        """
        Loads words from a specified file and organizes them by length.

        This function reads a file line by line, processes each word, and stores
        them in a dictionary where the key is the word length and the value is a list
        of words of that length. Words that are shorter than the minimum word length
        or contain non-alphabetical characters are ignored. The words are stored in
        uppercase. After loading, it prints the total number of words loaded.

        Args:
            file_path (str): The path to the file containing the list of words.
        """
        count = 0

        with open(file_path, "r") as file:
            for line in file:
                word = line.strip()

                if len(word) < self.MIN_WORD_LENGTH:
                    continue

                if word.isalpha():
                    length = len(word)

                    if length not in self.word_list:
                        self.word_list[length] = []

                    self.word_list[length].append(word.upper())
                    count += 1

        print(f"{Fore.CYAN}[INFO]{Fore.RESET} Loaded {count} words from \"{file_path}\"")

    def start(self, length: int):
        self.is_win = False

        if not self.__game_init(length):
            return None

        self.current_word = self.__get_random_word(length)

        return self.current_word

    def check(self, word: str):
        if len(word) != len(self.current_word):
            return 416

        if word.upper() not in self.word_list[len(self.current_word)]:
            return 404

        result = []
        # Mark which positions in the target string have been matched
        matched = [False] * len(word)

        # Find the exact match location (green)
        # Assume that all characters are correct
        all_correct = True
        for i in range(len(word)):
            if word[i].upper() == self.current_word[i]:
                result.append({word[i].upper(): Fore.GREEN})
                # Mark that the location is matched
                matched[i] = True
            else:
                # placeholders, to deal with later
                result.append(None)
                all_correct = False

        if all_correct:
            self.is_win = True
            return result

        # Count the unmatched letters in the target string (for yellow markers)
        available_letters = {}
        for i in range(len(self.current_word)):
            if not matched[i]:
                letter = self.current_word[i]
                available_letters[letter] = available_letters.get(letter, 0) + 1

        # Handle non-green locations
        for i in range(len(word)):
            if result[i] is not None:
                continue

            letter = word[i].upper()
            # Check if the letter is present and available
            if letter in available_letters and available_letters[letter] > 0:
                result[i] = {word[i].upper(): Fore.YELLOW}
                # Reduce the number of times you can use it
                available_letters[letter] -= 1
            else:
                result[i] = {word[i].upper(): Fore.RED}

        return result

    @staticmethod
    def input():
        """
        Prompts the user to enter a word, save the current cursor position, clears the current line, and then restores the cursor position.

        This function is used for getting user input in the middle of the console without messing up the console layout.

        Returns:
            str: The word that the user entered (in lowercase).
        """
        save_cursor_position()
        word = input("Enter a word > ").lower()
        clear_current_line()
        restore_cursor_position()

        return word

    def __game_init(self, length: int):
        if length < self.min_length or length > self.max_length:
            print(
                f"{Fore.RED}[ERROR]{Fore.RESET} The length can only be taken from {self.min_length} - {self.max_length}.")
            return False

        if length not in self.word_list:
            print(f"{Fore.RED}[ERROR]{Fore.RESET} There are no words with a length of {length}.")
            return False

        self.opportunity = length + 1
        return True

    def __get_random_word(self, length: int):
        return random.choice(self.word_list[length])

    def get_opportunity(self):
        return self.opportunity

    def deduction_opportunity(self, number: int):
        self.opportunity -= number

    def get_is_win(self):
        return self.is_win

    def get_current_word(self):
        return self.current_word
