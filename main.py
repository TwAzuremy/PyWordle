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

            ui.set_information("Start the game.")
            ui.set_other_msg(f"{Fore.CYAN}[Command]{Fore.RESET} {Fore.RED}/exit{Fore.RESET} - exit the game.")
            ui.set_debug(f"The current word is {Fore.GREEN + current_word + Fore.RESET}")

            # Build the UI
            ui.set_word_length(length)

            # Start the game
            while game.get_opportunity() > 0 and game.get_is_win() is False:
                ui.render()
                word = ui.input("Enter a word > ")

                # Instruction processing
                if word == "/exit":
                    break

                # Check the correctness of the words.
                result = game.check(word)

                # Exception handling
                if result == 404:
                    ui.set_information(f"{Fore.RED}'{word}'{Fore.RESET} does {Fore.RED}not exist{Fore.RESET} "
                                       f"in the word list.")
                    continue
                elif result == 416:
                    ui.set_information(f"The string you entered {Fore.RED}is not{Fore.RESET} "
                                       f"the correct length of {Fore.RED}'{word}'{Fore.RESET}.")
                    continue

                # If the word is correct, add .
                if result is not None:
                    game.deduction_opportunity(1)
                    ui.insert(result)

            # Game over
            ui.render()
            if game.get_is_win():
                print(f"\n{Fore.GREEN}You won the game!{Fore.RESET} The word was '{current_word}'.\n")
            else:
                print(f"\n{Fore.RED}You lost the game.{Fore.RESET} The word was '{current_word}'.\n")
