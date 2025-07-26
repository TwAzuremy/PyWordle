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
    
    # AI Battle mode support
    ai_battle_mode = False
    word_owners = []  # Track who made each guess: 'player' or 'ai'
    
    # Custom color definitions
    ORANGE_COLOR = '\033[38;2;255;127;80m'  # #FF7F50 Orange
    LIGHT_BLUE_COLOR = Fore.CYAN  # Light blue color same as INFO title

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

    def enable_ai_battle_mode(self):
        """Enable AI battle mode with special rendering"""
        self.ai_battle_mode = True
        
    def disable_ai_battle_mode(self):
        """Disable AI battle mode"""
        self.ai_battle_mode = False

    def clear(self):
        """Clears the list of words, resetting it to an empty state."""
        self.words = []
        self.word_owners = []

    def insert(self, word: list[dict[str, str]], owner: str = None):
        """
        Inserts a word into the list of words if its length matches the set word length.

        Args:
            word (list[dict[str, str]]): A list of dictionaries representing the word,
            where each dictionary contains a character as the key and its corresponding
            color as the value.
            owner (str): For AI battle mode, specify 'player' or 'ai'
        """
        if len(word) == self.length:
            self.words.append(word)
            if self.ai_battle_mode:
                self.word_owners.append(owner or 'player')

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
        # Initialize all required empty rows at the beginning
        empty_words = [[{" ": Fore.RESET} for _ in range(self.length)]
                       for _ in range(self.number - len(self.words))]
        empty_owners = ['empty'] * (self.number - len(self.words))

        print()
        all_words = self.words + empty_words
        all_owners = (self.word_owners if self.ai_battle_mode else []) + empty_owners
        
        for i, word in enumerate(all_words):
            owner = all_owners[i] if i < len(all_owners) else 'empty'
            rows = self.__build_rows(word, owner)
            for row in rows:
                print(row)

    def __build_rows(self, arr: list[dict[str, str]], owner: str = 'player'):
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
            owner (str): For AI battle mode, specify 'player', 'ai', or 'empty'

        Returns:
            list[str]: A list of three strings, representing the top, middle, and bottom
            rows of the word's visual representation.
        """
        # Determine box color
        if self.ai_battle_mode:
            # AI Battle mode: use fixed colors based on owner
            if owner == 'ai':
                box_color = self.LIGHT_BLUE_COLOR  # AI uses light blue boxes
            elif owner == 'player':
                box_color = self.ORANGE_COLOR  # Player uses orange boxes
            else:
                box_color = Fore.WHITE  # Empty slots use white
        else:
            # Main game mode: box color follows letter color, empty slots are white
            box_color = Fore.WHITE  # Default to white for empty slots
        
        # Build rows
        top_parts = []
        mid_parts = []
        bottom_parts = []
        
        for item in arr:
            letter = list(item.keys())[0]
            letter_color = list(item.values())[0]
            
            # In main game mode, if letter has color (not empty), box follows letter color
            if not self.ai_battle_mode and letter.strip() and letter_color != Fore.RESET:
                current_box_color = letter_color
            else:
                current_box_color = box_color
            
            # Build each part
            top_parts.append(f"{current_box_color}┌───┐{Fore.RESET}")
            mid_parts.append(f"{current_box_color}│{Fore.RESET} {letter_color}{letter}{Fore.RESET} {current_box_color}│{Fore.RESET}")
            bottom_parts.append(f"{current_box_color}└───┘{Fore.RESET}")
        
        top = ''.join(top_parts)
        mid = ''.join(mid_parts)
        bottom = ''.join(bottom_parts)

        return [top, mid, bottom]
