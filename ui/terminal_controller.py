import sys
import colorama

from colorama import Cursor
from typing import Optional, Union, List


class TerminalController:
    def __init__(self) -> None:
        colorama.init(autoreset=True)
        self.__commands = []
        self.__current_line = 1

    def clear_lines(self, start_line: int, end_line: Optional[int] = None) -> "TerminalController":
        if start_line < 1:
            raise ValueError("The line number must be greater than 0.")

        if end_line is None:
            self.__commands.append(Cursor.POS(1, start_line) + colorama.ansi.clear_line())
        else:
            if end_line < start_line:
                raise ValueError("The end line number must be greater than or equal to the start line number.")

            for line in range(start_line, end_line + 1):
                self.__commands.append(Cursor.POS(1, line) + colorama.ansi.clear_line())

        self.__current_line = end_line if end_line is not None else start_line

        return self

    def write_lines(self, start_line: int, content: Union[str, List[str]],
                    end_line: Optional[int] = None) -> "TerminalController":
        if start_line < 1:
            raise ValueError("The line number must be greater than 0.")

        if isinstance(content, str):
            content_lines = [content]
        elif isinstance(content, list) or isinstance(content, tuple):
            content_lines = content
        else:
            raise TypeError("The content must be a string or a list/tuple of strings.")

        if end_line is None:
            text = content_lines[0] if content_lines else ""
            self.__commands.append(
                Cursor.POS(1, self.__current_line)
                + colorama.ansi.clear_line()
                + str(text)
            )

            self.__current_line = start_line
        else:
            if end_line < start_line:
                raise ValueError("The end line number must be greater than or equal to the start line number.")

            total_lines = end_line - start_line + 1

            if len(content_lines) < total_lines:
                content_lines += [''] * (total_lines - len(content_lines))
            else:
                content_lines = content_lines[:total_lines]

            for i, text in enumerate(content_lines):
                line = start_line + i
                self.__commands.append(
                    Cursor.POS(1, line)
                    + colorama.ansi.clear_line()
                    + str(text)
                )

            self.__current_line = end_line

        return self

    def move_to(self, line: int, column: int = 1) -> "TerminalController":
        self.__commands.append(Cursor.POS(column, line))
        self.__current_line = line

        return self

    def write_at(self, line: int, column: int, text: str) -> "TerminalController":
        self.__commands.append(Cursor.POS(column, line) + text)
        self.__current_line = line

        return self

    def write(self, text: str) -> "TerminalController":
        self.__commands.append(text)

        return self

    def newline(self, count: int = 1) -> "TerminalController":
        self.__commands.append("\n" * count)
        self.__current_line += count

        return self

    def save_position(self):
        self.__commands.append(colorama.ansi.CSI + "s")

        return self

    def restore_position(self):
        self.__commands.append(colorama.ansi.CSI + "u")

        return self

    def flush(self) -> "TerminalController":
        if self.__commands:
            sys.stdout.write("".join(self.__commands))
            sys.stdout.flush()
            self.__commands = []

        return self

    def reset(self) -> "TerminalController":
        self.__commands = []

        return self

    def deinit(self):
        colorama.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()
