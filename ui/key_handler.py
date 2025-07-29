from typing import Dict

from blessed import Terminal


class KeyHandler:
    @staticmethod
    def register_menu(term: Terminal, menu: list[str], default_option: int = 0,
                      on_enter: callable = lambda x: None) -> int:
        current_selected = default_option
        on_enter(default_option)

        try:
            with term.cbreak(), term.hidden_cursor():
                while True:
                    key = term.inkey(timeout=0.1)

                    if repr(key) == "KEY_UP":
                        current_selected = (current_selected - 1) % len(menu)
                        on_enter(current_selected)
                    elif repr(key) == "KEY_DOWN":
                        current_selected = (current_selected + 1) % len(menu)
                        on_enter(current_selected)
                    elif key == "KEY_ENTER" or key == "\n" or key == "\r":
                        return current_selected
                    elif key == "KEY_ESCAPE" or key == "\x1b":
                        return current_selected
        finally:
            term.normal_cursor()

    @staticmethod
    def register_input(term: Terminal, default_text: str, on_render: callable = lambda x: None,
                       on_esc: callable = lambda: None, exit_on_esc: bool = False) -> str:
        text = default_text

        on_render(text, False)

        with term.cbreak():
            while True:
                key = term.inkey(timeout=0.1)

                if key == "KEY_ENTER" or key == "\n" or key == "\r":
                    break
                elif key == "KEY_BACKSPACE" or key == "\x7f":
                    text = text[:-1]
                elif key == "KEY_ESCAPE" or key == "\x1b":
                    if on_esc:
                        on_render(text, True)
                        is_exit = on_esc()

                    if exit_on_esc or is_exit == True or is_exit == '/exit':
                        return '/exit'

                elif key.is_sequence is False and key != "":
                    text += key

                on_render(text, False)

        return text

    @staticmethod
    def register_hotkey(term: Terminal, hotkey_list: list[Dict[str, any]], exit_key=None):
        def start_listening() -> str | None:
            with term.cbreak(), term.hidden_cursor():
                while True:
                    try:
                        key = term.inkey(timeout=0.1)

                        if not key:
                            continue

                        if exit_key is not None and exit_key(key):
                            break

                        for hotkey in hotkey_list:
                            if hotkey['condition'](key):
                                command = hotkey['func']()

                                if command == '/exit':
                                    return '/exit'
                    except KeyboardInterrupt:
                        break

                return None

        return start_listening
