from colorama import *
from utils import clear_console

import config
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
        clear_console()
        self.is_win = False

        self.__game_init(length)
        self.current_word = self.__get_random_word(length)

        if config.DEBUG:
            print(f"{Fore.RED}[DEBUG]{Fore.RESET} Current word: {self.current_word}")

    def check(self, word: str):
        if len(word) != len(self.current_word):
            print("The word must be the same length as the current word.")
            return None

        if word.upper() not in self.word_list[len(self.current_word)]:
            print("The word is not in the word list.")
            return None

        result = []
        # Mark which positions in the target string have been matched
        matched = [False] * len(word)

        # Find the exact match location (green)
        # Assume that all characters are correct
        all_correct = True
        for i in range(len(word)):
            if word[i].upper() == self.current_word[i]:
                result.append({word[i]: Fore.GREEN})
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
                result[i] = {word[i]: Fore.YELLOW}
                # Reduce the number of times you can use it
                available_letters[letter] -= 1
            else:
                result[i] = {word[i]: Fore.RED}

        return result

    def __game_init(self, length: int):
        if length < self.min_length or length > self.max_length:
            print(f"The length can only be taken from {self.min_length} - {self.max_length}.")
            return

        if length not in self.word_list:
            print(f"There are no words with a length of {length}.")
            return

        self.opportunity = length + 1

    def __get_random_word(self, length: int):
        return random.choice(self.word_list[length])

    def get_opportunity(self):
        return self.opportunity

    def deduction_opportunity(self, number: int):
        self.opportunity -= number

    def get_is_win(self):
        return self.is_win