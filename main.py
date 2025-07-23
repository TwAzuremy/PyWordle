from colorama import *
import argparse
import config

init(autoreset=True)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    config.DEBUG = args.debug

    from ui import UI
    from wordle import Wordle

    print(f"Debug: {config.DEBUG}")

    ui = UI()
    game = Wordle("word_list.txt")

    print(f"\n\t{Fore.GREEN}start{Fore.RESET} - start a new game\n\t{Fore.RED}exit{Fore.RESET} - exit the program\n")

    while True:
        ui.clear()

        command = input("PyWordle > ").lower()

        if command == "exit": break
        if command == "start":
            length = int(input("Enter the length of the word: "))
            game.start(length)
            ui.set_word_length(length)

            print(f"\n\t{Fore.RED}/exit{Fore.RESET} - exit the game\n")

            while game.get_opportunity() > 0 and game.get_is_win() is False:
                word = input(f"Enter your guess: ")

                if word == "/exit":
                    break

                result = game.check(word)

                if result is not None:
                    game.deduction_opportunity(1)
                    ui.insert(result)
                    ui.print()

            if game.get_is_win():
                print(f"\n\t{Fore.GREEN}You won!{Fore.RESET} The word was {game.current_word}!\n")
            else:
                print(f"\n\t{Fore.RED}You lost.{Fore.RESET} The word was {game.current_word}!\n")