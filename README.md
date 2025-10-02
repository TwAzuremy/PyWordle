# PyWordle - Terminal Word Game

## Play Wordle in Your Terminal!

PyWordle is a command-line implementation of the popular word-guessing game, featuring:

- 🎮 Classic Wordle gameplay with color-coded feedback
- 🌍 Multi-language support (English, Simplified/Traditional Chinese)
- ⚙️ Configurable word length for different difficulty levels
- 🎨 Colorful terminal interface with responsive design
- 🕹️ Intuitive keyboard controls

## Quick Start

1. Install requirements:

```bash
pip install -r requirements.txt
```

1. Run the game:

```bash
python main.py
```

1. Game controls:

- **↑/↓ arrows**: Navigate menus
- **Enter**: Confirm selection
- **Esc**: Go back/cancel
- **e**: Enter text editing mode
- **g**: Show current word (debug mode only)

## Configuration

Edit `config.txt` to customize:

```ini
MIN_WORD_LENGTH = 3
DEBUG = False
LANGUAGE = en_us  # Options: en_us, zh_cn, zh_tw
```

## Debug Mode

Enable special features with:

```bash
python main.py --debug
```

## Gameplay Preview

Best viewed with monospace font

```text
 > Player
   ┌───┐┌───┐┌───┐┌───┐┌───┐
 1 │ W ││ O ││ R ││ D ││ S │
   └───┘└───┘└───┘└───┘└───┘
   ┌───┐┌───┐┌───┐┌───┐┌───┐
 2 │   ││   ││   ││   ││   │
   └───┘└───┘└───┘└───┘└───┘
   ┌───┐┌───┐┌───┐┌───┐┌───┐
 3 │   ││   ││   ││   ││   │
   └───┘└───┘└───┘└───┘└───┘
   ┌───┐┌───┐┌───┐┌───┐┌───┐
 4 │   ││   ││   ││   ││   │
   └───┘└───┘└───┘└───┘└───┘
   ┌───┐┌───┐┌───┐┌───┐┌───┐
 5 │   ││   ││   ││   ││   │
   └───┘└───┘└───┘└───┘└───┘
   ┌───┐┌───┐┌───┐┌───┐┌───┐
 6 │   ││   ││   ││   ││   │
   └───┘└───┘└───┘└───┘└───┘

[INFO] The game begins, please enter a word with a length of 5.

Press esc to stop editing, enter to confirm.
┌Input────────────────────────────────────────────────────────┐
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Enjoy guessing words directly in your terminal!
