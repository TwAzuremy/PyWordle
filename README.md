# PyWordle - Terminal Wordle Game

PyWordle is a Python implementation of the popular Wordle game, designed to run in your terminal. It features a colorful interface, adjustable word lengths, and a classic Wordle gameplay experience.

## Features

- 🎮 Classic Wordle gameplay in your terminal
- 🎨 Colorful feedback using Colorama
- 🔢 Adjustable word lengths (3+ letters)
- 🧠 Smart word validation and hint system
- 🐛 Debug mode for testing
- 📱 Responsive terminal UI

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pywordle.git
cd pywordle
```

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

1. Prepare a word list file:

   - Create a file named `word_list.txt`

   - Add one word per line (all lowercase)

   - Example:

     ```text
     apple
     zebra
     python
     ```

## How to Play

1. Start the game:

```bash
python main.py
```

1. Game commands:
   - `start <length>` - Start a new game with specified word length
   - `exit` - Exit the program
   - `/exit` - Exit current game (during gameplay)
2. During gameplay:
   - Guess words of the correct length
   - Receive color-coded feedback:
     - 🟩 Green: Correct letter in correct position
     - 🟨 Yellow: Correct letter in wrong position
     - 🟥 Red: Letter not in word
   - You have (word length + 1) attempts

## Debug Mode

Run with debug mode to see the solution:

```bash
python main.py --debug
```

## File Structure

```text
pywordle/
├── main.py          # Main game entry point
├── ui.py            # User interface components
├── wordle.py        # Game logic implementation
├── utils.py         # Utility functions
├── config.py        # Configuration settings
└── word_list.txt    # Word database (create your own)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any:

- Bug fixes
- New features
- Documentation improvements

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/TwAzuremy/PyWordle/blob/master/LICENSE) file for details.