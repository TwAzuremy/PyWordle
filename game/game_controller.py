import config.config as config

from typing import Dict
from colorama import Fore

from ui.ui import UI
from game.wordle import Wordle
from utils.utils import hotkey_style
from error import LengthNotExist, LetterNotExist
from .menu_enum import *


class GameController:
    def __init__(self):
        self.ui = UI()
        self.ui.set_banner("banner.txt")
        self.game = Wordle("word_list.txt")
        self.__state = self.__render_cover

    def run(self):
        while True:
            command = self.__state()

            match command:
                case '#cover':
                    self.__state = self.__render_cover
                case '#start':
                    self.__state = self.__render_form
                case '#options':
                    self.__state = lambda: self.__render_options(MenuEnum.OPTIONS_MENU, 0)
                case '#language':
                    self.__state = lambda: self.__render_options(MenuEnum.OPTIONS_LANGUAGE, 0)
                case '/exit':
                    print("\n\n")
                    break

    def __render_cover(self) -> any:
        menu = MenuEnum.COVER_MENU.value

        self.ui.hotkey_tip = f"Press {hotkey_style('↑↓')} to select, {hotkey_style('enter')} to confirm, {hotkey_style('Esc')} to back."
        option_result = self.ui.render_cover(menu, 1)

        # Run the selected option.
        index = menu[option_result]['func']()

        if index == -1:
            return '/exit'

        return index

    def __render_options(self, menu: MenuEnum, selected: int = 0):
        value = menu.value
        result = self.ui.render_menu(value, 1, selected)

        index = value[result]['func']()

        if index == -1:
            return None

        return index

    def __render_form(self) -> None:
        self.ui.clear_screen()
        title = "Enter─the─word─length"

        while True:
            string = self.ui.input(
                title,
                f"Press {hotkey_style('Esc')} to return to the menu, {hotkey_style('Enter')} to confirm.",
                "",
                None,
                exit_on_esc=True
            )

            if string == '/exit':
                self.__state = self.__render_cover
                return None

            try:
                length = int(string)
                self.game.start(length)

                self.__state = self.__render_game
                break
            except ValueError:
                self.ui.set_information("Invalid input please try again", "error")
            except (LengthNotExist, LetterNotExist) as e:
                self.ui.set_information(str(e), "error")

        return None

    def __render_game(self) -> None:
        hotkey, input_tip, shortcut_tip = self.__build_game_hotkey()
        length = self.game.get_length()

        self.ui.render_game_structure(
            length,
            f" > {Fore.YELLOW}Player{Fore.RESET}",
            "Start the game.",
            input_tip
        )

        while self.game.get_chance() > 0 and not self.game.get_win_status():
            letter = self.ui.input("Input", input_tip, shortcut_tip, hotkey)

            if letter == '/exit':
                break

            try:
                color_letter = self.game.check(letter)
                self.game.reduce_chance()
                self.ui.append(color_letter, length - self.game.get_chance() + 1)
            except (LengthNotExist, LetterNotExist) as e:
                self.ui.set_information(str(e), "error")
                continue

        self.__state = self.__render_over
        return None

    def __render_over(self) -> None:
        hotkey, _, shortcut_tip = self.__build_game_hotkey()
        input_tip = f"Press {hotkey_style('Esc')} to stop editing, {hotkey_style('Enter')} to return menu."

        if self.game.get_win_status():
            self.ui.set_information(f"{Fore.GREEN}You win!{Fore.RESET} The word is: {self.game.get_word()}.")
        else:
            self.ui.set_information(f"{Fore.RED}You lose!{Fore.RESET} The word is: {self.game.get_word()}.")

        self.ui.input("Input", input_tip, shortcut_tip, hotkey)
        self.game.end()

        self.__state = self.__render_cover
        return None

    def __build_game_hotkey(self) -> tuple[list[Dict[str, any]], str, str]:
        hotkey = [
            {
                "key": "q",
                "condition": lambda key: key == "q",
                "description": "exit",
                "func": lambda: '/exit'
            },
            {
                "key": "↑↓",
                "condition": lambda key: repr(key) == "KEY_UP",
                "description": "scroll area",
                "func": lambda: self.ui.scroll_display_area('up', 2)
            },
            {
                "key": "",
                "condition": lambda key: repr(key) == "KEY_DOWN",
                "description": "",
                "func": lambda: self.ui.scroll_display_area('down', 2)
            }
        ]

        if config.DEBUG:
            hotkey.append({
                "key": "g",
                "condition": lambda key: key == "g",
                "description": "get the word",
                "func": lambda: self.ui.set_information(f"The word for the current game is: "
                                                        f"{Fore.GREEN}{self.game.get_word()}.", "debug")
            })

        tip_1 = f"Press {hotkey_style('Esc')} to stop editing, {hotkey_style('Enter')} to confirm."
        tip_2 = (f"Press "
                 + f"{hotkey_style('e')} to start editing, "
                 + ', '.join(
                    f"{hotkey_style(hk['key'])} to {hk['description']}"
                    for hk in hotkey
                    if hk['key'] != ''
                ) + ".")

        return hotkey, tip_1, tip_2
