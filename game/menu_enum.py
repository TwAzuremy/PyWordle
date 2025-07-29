from enum import Enum


class MenuEnum(Enum):
    COVER_MENU = [
        {
            'name': 'Start',
            'description': 'Start a new game',
            'func': lambda: '#start'
        },
        {
            'name': 'Options',
            'description': 'Game options',
            'func': lambda: '#options'
        },
        {
            'name': 'Exit',
            'description': 'Exit the game',
            'func': lambda: '/exit'
        }
    ]

    OPTIONS_MENU = [
        {
            'name': 'Language',
            'description': 'Select the language',
            'func': lambda: '#language'
        },
        {
            'name': 'Exit',
            'description': 'Exit the game',
            'func': lambda: '/exit'
        }
    ]

    OPTIONS_LANGUAGE = [
        {
            'name': 'English',
            'description': 'Select the language',
            'func': lambda: '#language'
        },
        {
            'name': 'Exit',
            'description': 'Exit the game',
            'func': lambda: '/exit'
        }
    ]
