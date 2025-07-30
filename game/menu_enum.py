from enum import Enum
from typing import Dict

from lang.language import lang


class MenuEnum:
    @staticmethod
    def cover_menu() -> list[Dict[str, any]]:
        return [
            {
                'name': lang.get('cover.menu.start'),
                'description': 'Start a new game',
                'func': lambda: '#start'
            },
            {
                'name': lang.get('cover.menu.options'),
                'description': 'Game options',
                'func': lambda: '#options'
            },
            {
                'name': lang.get('cover.menu.exit'),
                'description': 'Exit the game',
                'func': lambda: '/exit'
            }
        ]

    @staticmethod
    def options_menu() -> list[Dict[str, any]]:
        return [
            {
                'name': lang.get('options.menu.language'),
                'description': 'Select the language',
                'func': lambda: '#language'
            },
            {
                'name': lang.get('menu.back'),
                'description': 'Return to the previous menu',
                'func': lambda: '#cover'
            }
        ]

    @staticmethod
    def options_language_menu() -> list[Dict[str, any]]:
        return [
            {
                'name': lang.get('menu.back'),
                'description': 'Return to the previous menu',
                'func': lambda: '#options'
            }
        ]
