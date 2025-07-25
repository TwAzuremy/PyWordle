
# PyWordle - Terminal Wordle Game

PyWordle is a Python implementation of the popular Wordle game, designed to run in your terminal. It features a colorful interface, adjustable word lengths, intelligent AI opponents, and a classic Wordle gameplay experience.

## Features

- 🎮 Classic Wordle gameplay in your terminal
- 🤖 **AI Battle Mode** with three difficulty levels
- 🎨 Colorful feedback using Colorama
- 🔢 Adjustable word lengths (3+ letters)
- 🧠 Smart word validation and intelligent hint system
- 🎯 Strategic AI opponents with advanced algorithms
- 🐛 Debug mode for testing
- 📱 Responsive terminal UI

## Game Modes

### 🎮 Classic Mode

Traditional single-player Wordle experience with intelligent hints.

### 🤖 AI Battle Mode

Compete against intelligent AI opponents with three difficulty levels:

- **🟢 Easy AI**: Basic reasoning with letter frequency analysis
- **🟡 Medium AI**: Information theory optimization with entropy calculations
- **🔴 Hard AI**: Advanced game theory with Monte Carlo tree search

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pywordle.git
cd pywordle
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Prepare a word list file:

   - Create a file named `word_list.txt`
   - Add one word per line (all lowercase)
   - Example:

     ```text
     apple
     zebra
     python
     ```

## How to Play

### Classic Mode

1. Start the classic game:

```bash
python main.py
```

2. Game commands:

   - `start <length>` - Start a new game with specified word length
   - `exit` - Exit the program
3. During gameplay:

   - `/exit` - Exit current game
   - `/hint` - Get an intelligent word suggestion
   - Guess words of the correct length
   - Receive color-coded feedback:
     - 🟩 Green: Correct letter in correct position
     - 🟨 Yellow: Correct letter in wrong position
     - 🟥 Red: Letter not in word
   - You have (word length + 1) attempts

### AI Battle Mode

1. Start AI battle:

```bash
python ai_battle.py
```

2. Select AI difficulty and word length
3. Compete turn-by-turn against the AI
4. First player to guess correctly wins!

## Intelligent Hint System

The enhanced hint system provides strategic word suggestions by:

- Analyzing all previous guesses and feedback
- Considering confirmed positions, required letters, and forbidden letters
- Handling duplicate letters with precise count constraints
- Ranking candidates based on letter frequency and information gain
- Providing balanced selection from top-scoring candidates

## AI Algorithms

### Easy AI

- Constraint-based reasoning
- Basic letter frequency analysis
- Simple pattern matching

### Medium AI

- Information theory with entropy calculations
- Advanced frequency analysis (letter + position)
- Adaptive strategy based on remaining attempts

### Hard AI

- Game theory with strategic concealment
- Monte Carlo tree search for future state simulation
- Multi-layered decision algorithm:
  - Strategic opening with balanced information/stealth
  - Entropy-maximizing midgame strategies
  - Endgame optimization
- Advanced pattern recognition with bigram analysis
- Cached entropy calculations for performance

## Debug Mode

Run with debug mode to see the solution:

```bash
python main.py --debug
python ai_battle.py --debug
```

## File Structure

```text
pywordle/
├── main.py          # Classic game entry point
├── ai_battle.py     # AI battle mode with intelligent opponents
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
- AI algorithm improvements
- Documentation improvements

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/TwAzuremy/PyWordle/blob/master/LICENSE) file for details.
