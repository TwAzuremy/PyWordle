import random

from colorama import Fore
from error import LengthNotExist, LetterNotExist
from config.config import config
from lang.language import lang
from utils.utils import *


class Wordle:
    __word_list = {}
    __chance = 0
    __word = ''

    __win_status = False

    def __init__(self, file_path: str) -> None:
        self.__process_file(file_path)

        self.__min_length = min(self.__word_list.keys())
        self.__max_length = max(self.__word_list.keys())

    def __process_file(self, file_path: str) -> int:
        """
        Process the given file to store words of different lengths in the internal word list.

        This method reads the given file line by line, strips the line of leading and trailing
        whitespace, and checks if the length of the word is greater than or equal to the minimum
        word length set in the configuration and if the word consists of only alphabetic characters.
        If the word passes the check, it is added to the internal word list with its length as the key.
        The number of words processed is returned.

        :param file_path: The path to the file to be processed.
        :type file_path: str

        :returns: The number of words processed.
        :rtype: int
        """
        count = 0

        with open(file_path) as f:
            for line in f:
                word = line.strip()

                if len(word) >= config.get("MIN_WORD_LENGTH", 3) and word.isalpha():
                    self.__word_list.setdefault(len(word), []).append(word)
                    count += 1

        return count

    def start(self, length: int) -> None:
        if length < self.__min_length or length > self.__max_length:
            raise LengthNotExist(
                format_string(lang.get("wordle.start.length_not_exist"), length, self.__min_length, self.__max_length))

        if length not in self.__word_list:
            raise LetterNotExist(format_string(lang.get("wordle.start.letter_not_exist"), length))

        self.__word = self.__random(length)
        self.__chance = length + 1

    def end(self):
        self.__win_status = False
        self.__word = ''
        self.__chance = 0

    def check(self, word: str) -> list[dict[str, str]]:
        if len(word) != len(self.__word):
            raise LengthNotExist(
                format_string(lang.get("wordle.check.length_not_exist"), f"{Fore.RED}{word}{Fore.RESET}",
                              f"{Fore.GREEN}{len(self.__word)}{Fore.RESET}"))

        if word.upper() not in self.__word_list[len(word)]:
            raise LetterNotExist(
                format_string(lang.get("wordle.check.letter_not_exist"), f"{Fore.RED}{word}{Fore.RESET}"))

        result = []
        matched = [False] * len(self.__word)
        # Find the exact match location (Green)
        # Assume that all char are correct
        all_correct = True
        for i in range(len(word)):
            if word[i].upper() == self.__word[i].upper():
                result.append({word[i].upper(): Fore.GREEN})
                # Mark that the location is matched
                matched[i] = True
            else:
                # placeholders, to deal with later
                result.append(None)
                all_correct = False

        if all_correct:
            self.__win_status = True
            return result

        # Count the unmatched letters in the target string (Yellow)
        available_letters = {}
        for i in range(len(self.__word)):
            if not matched[i]:
                letter = self.__word[i].upper()
                available_letters[letter] = available_letters.get(letter, 0) + 1

        # Handle non-green locations (Red)
        for i in range(len(word)):
            if result[i] is not None:
                continue

            letter = word[i].upper()
            # Check if the letter is present and available
            if letter in available_letters and available_letters[letter] > 0:
                result[i] = {word[i].upper(): Fore.YELLOW}
                available_letters[letter] -= 1
            else:
                result[i] = {word[i].upper(): Fore.RED}

        return result

    def reduce_chance(self) -> None:
        """
        Reduces the current chance remaining in the game by one.

        This method simply decrements the current chance remaining in the game by one.

        :rtype: None
        """
        self.__chance -= 1

    def get_chance(self) -> int:
        """
        Returns the current chance remaining in the game.

        :returns: The current chance remaining in the game.
        :rtype: int
        """
        return self.__chance

    def get_length(self) -> int:
        return len(self.__word)

    def get_word(self) -> str:
        """
        Returns the current word in the game.

        :returns: The current word in the game.
        :rtype: str
        """
        return self.__word

    def get_win_status(self) -> bool:
        return self.__win_status

    def __init(self, length: int):
        pass

    def __random(self, length: int) -> str:
        """
        Selects a random word of the specified length from the internal word list.

        This method uses the random.choice function to return a word from the list
        of words that match the given length. It assumes that the list for the specified
        length is non-empty.

        :param length: The length of the word to be selected.
        :type length: int

        :returns: A randomly selected word of the specified length.
        :rtype: str
        """
        return random.choice(self.__word_list[length])
