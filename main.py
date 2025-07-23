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

    ui = UI()
    game = Wordle("word_list.txt")

    while True:
        ui.clear()
        print(f"\n\t{Fore.GREEN}start{Fore.RESET} <word length> - start a new game"
              f"\n\t{Fore.RED}exit{Fore.RESET} - exit the program\n")

        command = input("PyWordle > ").strip().split()

        # Instruction processing
        if command[0].lower() == "exit": break
        if command[0].lower() == "start":
            try:
                length = int(command[1])
            except IndexError:
                length = int(input("Enter the length of the word > "))

            current_word = game.start(length)

            if current_word is None:
                continue

            # Build the UI
            ui.set_word_length(length)
            ui.build_empty_table(f"Start the game.",
                                 f"{Fore.CYAN}[Command]{Fore.RESET} {Fore.RED}/exit{Fore.RESET} - exit the game.")

            # debug: Get the current word.
            ui.print_debug(f"The current word is {Fore.GREEN + current_word + Fore.RESET}")

            # Start the game
            while game.get_opportunity() > 0 and game.get_is_win() is False:
                word = game.input()

                # Instruction processing
                if word == "/exit":
                    break

                result = game.check(word)

                # Exception handling
                if result == 404:
                    ui.print_info(f"The word {Fore.RED}is not{Fore.RESET} in the {Fore.RED}word list{Fore.RESET}.")
                    continue
                elif result == 416:
                    ui.print_info(f"The word {Fore.RED}must be the same length{Fore.RESET} as the current word.")
                    continue

                # If the word is correct, add .
                if result is not None:
                    game.deduction_opportunity(1)
                    ui.insert(result)

            # Game over
            if game.get_is_win():
                ui.print_info(f"{Fore.GREEN}You won the game!{Fore.RESET} The word was '{current_word}'.")
            else:
                ui.print_info(f"{Fore.RED}You lost the game.{Fore.RESET} The word was '{current_word}'.")