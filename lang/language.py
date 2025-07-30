from config.config import config
from utils.utils import load_key_value_file
from colorama import Fore


class Language:
    __mapping = {}

    def __init__(self, file_path: str):
        self.__load_mapping(file_path)

    def __load_mapping(self, file_path: str):
        """
        Loads the language mappings from the specified file.

        Reads the file line by line, skipping empty lines and comments. For each valid line,
        the key-value pairs are extracted and stored in the `__mapping` dictionary.

        :param file_path: The path to the language configuration file.
        """
        self.__mapping = load_key_value_file(file_path)

    def find_key_index(self) -> int:
        """
        Finds the index of the current language key in the mapping.

        This method compares the current language key (retrieved from the config) with the
        keys in the `__mapping` dictionary and returns the index of the current language.

        :return: The index of the current language key in the list of available keys. Defaults to 0 if not found.
        """
        keys = list(self.__mapping.keys())

        try:
            return keys.index(config.get("LANGUAGE", "en_us"))
        except ValueError:
            return 0

    def build_option_menu(self) -> list[dict]:
        """
        Builds an option menu for selecting a language.

        Generates a list of dictionaries representing each language option. Each option
        includes a name (with highlighting for the current language) and a function
        to change the selected language when clicked.

        :return: A list of dictionaries representing language options, including the language name, description,
                 and a function to set the selected language in the config.
        """
        current = config.get("LANGUAGE", "en_us")

        return [{
            'name': f"{Fore.YELLOW if code == current else ''}{name}{Fore.RESET}",
            'description': '',
            'func': lambda c=code: config.set("LANGUAGE", c, True)
        } for code, name in self.__mapping.items()]


lang = Language("lang_mapping.txt")
