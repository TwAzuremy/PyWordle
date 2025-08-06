import os

from utils.utils import *


class ConfigManager:
    def __init__(self, file_path: str | Path):
        """
        Initializes the ConfigManager with the given configuration file path.

        :param file_path: The path to the configuration file to load.
        """
        self.file_path = file_path
        self.config = {}  # Stores the parsed configuration key-value pairs
        self.raw_lines = []  # Stores the raw lines from the file, including comments and empty lines
        self.key_positions = {}  # Stores the line positions of each key in the file
        self.__load_config()

    def __load_config(self):
        """
        Loads the configuration file and parses its contents.

        Reads the configuration file, processes each line, and populates the
        `config` dictionary with key-value pairs. It also tracks the positions
        of keys in the file to support modification and saving.
        """
        if not os.path.exists(self.file_path):
            return

        with open(self.file_path, 'r') as f:
            self.raw_lines = f.readlines()

        for idx, line in enumerate(self.raw_lines):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Process key-value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Convert the value to an appropriate type
                self.config[key] = self.__convert_value(value)
                # Record the line position of the key
                self.key_positions[key] = idx

    def __convert_value(self, value) -> any:
        """
        Tries to convert a string value to an appropriate data type (int, float, bool, or str).

        :param value: The string value to be converted.
        :return: The converted value in the appropriate data type.
        """
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                if value.lower() == 'true':
                    return True
                elif value.lower() == 'false':
                    return False
                else:
                    # Keep the original string if it can't be converted
                    return value

    def get(self, key: str, default: any = None) -> any:
        """
        Retrieves the value of the specified configuration key.

        :param key: The configuration key to fetch.
        :param default: The default value to return if the key is not found.
        :return: The value of the key if found, otherwise the default value.
        """
        return self.config.get(key, default)

    def set(self, key: str, value: any, save_immediately: bool = False):
        """
        Sets a configuration key to a new value.

        Updates the in-memory configuration dictionary and modifies the corresponding
        line in the raw configuration data. If the key is new, it will be added.

        :param key: The configuration key to set.
        :param value: The new value to assign to the key.
        :param save_immediately: Whether to save the changes to the file immediately.
        """
        # Update the in-memory configuration
        self.config[key] = value

        # Update the raw lines
        new_line = f"{key} = {value}\n"

        if key in self.key_positions:
            # Update the existing key's line
            idx = self.key_positions[key]
            self.raw_lines[idx] = new_line
        else:
            # Add a new key
            self.raw_lines.append(new_line)
            self.key_positions[key] = len(self.raw_lines) - 1

        # Optionally save the configuration to the file
        if save_immediately:
            self.save()

    def save(self):
        """
        Saves the current configuration to the file.

        Writes the entire content of `raw_lines` (which includes all keys and their values)
        back to the configuration file.
        """
        with open(self.file_path, 'w') as f:
            f.writelines(self.raw_lines)


config = ConfigManager(get_resource_path(f"{RESOURCES_PATH}/config.txt"))
DEBUG = config.get("DEBUG", False)
