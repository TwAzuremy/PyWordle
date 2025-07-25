from colorama import *

import random


class Wordle:
    MIN_WORD_LENGTH = 3

    word_list = {}

    is_win = False
    current_word = ""
    opportunity = 0
    guess_history = []  # Store guess history

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
        self.guess_history = []  # Reset guess history.

        if not self.__game_init(length):
            return None

        self.current_word = self.__get_random_word(length)

        return self.current_word

    def check(self, word: str):
        if len(word) != len(self.current_word):
            return 416

        if word.upper() not in self.word_list[len(self.current_word)]:
            return 404

        # Add guess history
        self.guess_history.append(word.upper())

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

    def get_tip(self):
        word_length = len(self.current_word)

        # If not guess history, return a random word that meets the length requirements.
        if not self.guess_history:
            return random.choice(self.word_list[word_length])

        # Analyze the guessed vocabulary to gain known information.
        confirmed_letters = {}  # Letters determine the position {position: letter}
        excluded_letters = set()  # Excluded letters
        possible_letters = set()  # Possible letters included
        wrong_positions = {}  # Letters cannot be in the designated positions. {letter: [position list]}

        for guess in self.guess_history:
            result = self._analyze_guess(guess)

            for i, (letter, color) in enumerate(result):
                if color == Fore.GREEN:
                    confirmed_letters[i] = letter
                elif color == Fore.YELLOW:
                    possible_letters.add(letter)
                    if letter not in wrong_positions:
                        wrong_positions[letter] = []
                    wrong_positions[letter].append(i)
                elif color == Fore.RED:
                    excluded_letters.add(letter)

        # Select the words that meet the criteria from the word list
        candidates = []
        for word in self.word_list[word_length]:
            if word in self.guess_history:
                continue  # Skip the words that have already been guessed

            is_valid = True

            # Check and confirm the letter of the position
            for pos, letter in confirmed_letters.items():
                if word[pos] != letter:
                    is_valid = False
                    break

            if not is_valid:
                continue

            # Check if it contains possible letters and not in wrong positions
            word_letters = set(word)
            if not possible_letters.issubset(word_letters):
                is_valid = False

            # Check that yellow letters are not in wrong positions
            for letter, positions in wrong_positions.items():
                for pos in positions:
                    if word[pos] == letter:
                        is_valid = False
                        break
                if not is_valid:
                    break

            # Check if it contains excluded letters
            if word_letters.intersection(excluded_letters):
                is_valid = False

            if is_valid:
                candidates.append(word)

        # If no qualifying candidates are found, return a random word
        if not candidates:
            remaining_words = [w for w in self.word_list[word_length] if w not in self.guess_history]
            if remaining_words:
                return random.choice(remaining_words)
            else:
                return random.choice(self.word_list[word_length])

        # Return a random one from the candidates
        return random.choice(candidates)

    def _analyze_guess(self, guess):
        """
        Analyze the guess result and return color information for each letter

        Args:
            guess (str): The guessed word

        Returns:
            list: [(letter, color), ...]
        """
        result = []
        matched = [False] * len(guess)

        # Find exact match positions (green)
        for i in range(len(guess)):
            if guess[i] == self.current_word[i]:
                result.append((guess[i], Fore.GREEN))
                matched[i] = True
            else:
                result.append((guess[i], None))

        # Count unmatched letters in the target word
        available_letters = {}
        for i in range(len(self.current_word)):
            if not matched[i]:
                letter = self.current_word[i]
                available_letters[letter] = available_letters.get(letter, 0) + 1

        # Handle non-green positions
        for i in range(len(guess)):
            if result[i][1] is not None:
                continue

            letter = guess[i]
            if letter in available_letters and available_letters[letter] > 0:
                result[i] = (letter, Fore.YELLOW)
                available_letters[letter] -= 1
            else:
                result[i] = (letter, Fore.RED)

        return result
