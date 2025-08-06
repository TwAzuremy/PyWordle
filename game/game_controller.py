import config.config as config

from ui.ui import UI
from game.wordle import Wordle
from utils.utils import *
from error import LengthNotExist, LetterNotExist
from .menu_enum import *
from lang.language import lang


class GameController:
    def __init__(self):
        self.ui = UI()
        self.ui.set_banner(get_resource_path(f"{RESOURCES_PATH}/banner.txt"))
        self.game = Wordle(get_resource_path("word_list.txt"))
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
                    self.__state = lambda: self.__render_options(MenuEnum.options_menu(), 0)
                case '#language':
                    self.__state = lambda: self.__render_options(
                        lang.build_option_menu() + MenuEnum.options_language_menu(), lang.find_key_index()
                    )
                case '/exit':
                    print("\n\n")
                    break

    def __render_cover(self) -> any:
        menu = MenuEnum.cover_menu()

        self.ui.hotkey_tip = format_string(lang.get("cover.hotkey.tip"), hotkey_style('↑↓'), hotkey_style('enter'),
                                           hotkey_style('esc'))
        option_result = self.ui.render_cover(menu, 1)

        # Run the selected option.
        index = menu[option_result]['func']()

        if index == -1:
            return '/exit'

        return index

    def __render_options(self, menu: list, selected: int = 0):
        result = self.ui.render_menu(menu, 1, selected)

        index = menu[result]['func']()

        if index == -1:
            return None

        return index

    def __render_form(self) -> None:
        self.ui.clear_screen()
        title = lang.get("form.title")

        while True:
            string = self.ui.input(
                title,
                format_string(lang.get("form.hotkey.tip"), hotkey_style('esc'), hotkey_style('enter')),
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
                self.ui.set_information(lang.get("form.input.invalid_input"), "error")
            except (LengthNotExist, LetterNotExist) as e:
                self.ui.set_information(str(e), "error")

        return None

    def __render_game(self) -> None:
        hotkey, input_tip, shortcut_tip = self.__build_game_hotkey()
        length = self.game.get_length()

        self.ui.render_game_structure(
            length,
            f" > {Fore.YELLOW}{lang.get('game.display.player')}{Fore.RESET}",
            format_string(lang.get("game.information.start"), f"{Fore.GREEN}{length}{Fore.RESET}"),
            input_tip
        )

        while self.game.get_chance() > 0 and not self.game.get_win_status():
            letter = self.ui.input(lang.get("game.input.title"), input_tip, shortcut_tip, hotkey)

            if letter.replace(" ", "") == '':
                continue

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
        input_tip = format_string(lang.get("over.input.hotkey.tip"), hotkey_style('esc'), hotkey_style('enter'))

        word = self.game.get_word()
        if self.game.get_win_status():
            self.ui.set_information(
                f"{Fore.GREEN}{lang.get('over.status.win')}{Fore.RESET} {format_string(lang.get('over.status.word'), word)}")
        else:
            self.ui.set_information(
                f"{Fore.RED}{lang.get('over.status.lose')}{Fore.RESET} {format_string(lang.get('over.status.word'), word)}")

        self.ui.input(lang.get("over.input.title"), input_tip, shortcut_tip, hotkey)
        self.game.end()

        self.__state = self.__render_cover
        return None

    def __build_game_hotkey(self) -> tuple[list[Dict[str, any]], str, str]:
        hotkey = [
            {
                "key": "q",
                "condition": lambda key: key == "q",
                "description": lang.get("game.input.hotkey.exit"),
                "func": lambda: '/exit'
            },
            {
                "key": "↑↓",
                "condition": lambda key: repr(key) == "KEY_UP",
                "description": lang.get("game.input.hotkey.scroll"),
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
                "description": lang.get("debug.game.input.hotkey.get_word"),
                "func": lambda: self.ui.set_information(
                    format_string(lang.get("debug.game.information.get_word"), f"{Fore.GREEN}{self.game.get_word()}"),
                    "debug")
            })

        tip_1 = format_string(lang.get("game.input.hotkey.tip"), hotkey_style('esc'), hotkey_style('enter'))
        tip_2 = (f"{lang.get('game.input.hotkey.tip.press')} "
                 + f"{hotkey_style('e')} {lang.get('game.input.hotkey.tip.start_editing')}, "
                 + ', '.join(
                    f"{hotkey_style(hk['key'])} {hk['description']}"
                    for hk in hotkey
                    if hk['key'] != ''
                ) + ".")

        return hotkey, tip_1, tip_2
