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
            ui.set_other_msg(f"{Fore.CYAN}[Command]{Fore.RESET} {Fore.RED}/exit{Fore.RESET} - exit the game, {Fore.YELLOW}/hint{Fore.RESET} - get a hint.")
            ui.set_debug(f"The current word is {Fore.GREEN + current_word + Fore.RESET}")

            # Build the UI
            ui.set_word_length(length)

            # Initialize invalid input counter
            invalid_input_count = 0
            max_invalid_attempts = 3

            # Start the game
            while game.get_opportunity() > 0 and game.get_is_win() is False:
                # Display remaining attempts and invalid input warnings
                remaining_attempts = game.get_opportunity()
                remaining_invalid_attempts = max_invalid_attempts - invalid_input_count
                
                if invalid_input_count > 0:
                    ui.set_other_msg(f"{Fore.CYAN}[Command]{Fore.RESET} {Fore.RED}/exit{Fore.RESET} - exit the game, {Fore.YELLOW}/hint{Fore.RESET} - get a hint.\n"
                                     f"{Fore.RED}Invalid attempts [{invalid_input_count}/{max_invalid_attempts}]{Fore.RESET}")
                else:
                    ui.set_other_msg(f"{Fore.CYAN}[Command]{Fore.RESET} {Fore.RED}/exit{Fore.RESET} - exit the game, {Fore.YELLOW}/hint{Fore.RESET} - get a hint.")
                
                ui.render()
                word = ui.input(f"Enter a word (Attempts left: {Fore.CYAN}{remaining_attempts}{Fore.RESET}) > ")

                # Instruction processing
                if word == "/exit":
                    break
                elif word == "/hint":
                    tip_word = game.get_tip()
                    ui.set_information(f"{Fore.YELLOW}Hint:{Fore.RESET} Try the word '{Fore.CYAN}{tip_word.lower()}{Fore.RESET}'")
                    continue

                # Check the correctness of the words.
                result = game.check(word)

                # Exception handling
                if result == 404:
                    invalid_input_count += 1
                    remaining_invalid_attempts = max_invalid_attempts - invalid_input_count
                    
                    if invalid_input_count >= max_invalid_attempts:
                        ui.set_information(f"{Fore.RED}GAME OVER!{Fore.RESET} Too many invalid words [{max_invalid_attempts}/{max_invalid_attempts}].")
                        ui.set_other_msg("")  # Clear other messages when game ends
                        ui.render()
                        print(f"\n{Fore.RED}You lost the game due to too many invalid inputs!{Fore.RESET} The word was '{current_word}'.\n")
                        break
                    else:
                        ui.set_information(f"{Fore.RED}'{word}'{Fore.RESET} not in word list. Invalid attempts [{invalid_input_count}/{max_invalid_attempts}]")
                    continue
                elif result == 416:
                    invalid_input_count += 1
                    remaining_invalid_attempts = max_invalid_attempts - invalid_input_count
                    
                    if invalid_input_count >= max_invalid_attempts:
                        ui.set_information(f"{Fore.RED}GAME OVER!{Fore.RESET} Too many invalid words [{max_invalid_attempts}/{max_invalid_attempts}].")
                        ui.set_other_msg("")  # Clear other messages when game ends
                        ui.render()
                        print(f"\n{Fore.RED}You lost the game due to too many invalid inputs!{Fore.RESET} The word was '{current_word}'.\n")
                        break
                    else:
                        ui.set_information(f"Wrong length '{Fore.RED}{word}{Fore.RESET}'. Invalid attempts [{invalid_input_count}/{max_invalid_attempts}]")
                    continue

                # Reset invalid input counter on valid input
                invalid_input_count = 0

                # If the word is correct, add .
                if result is not None:
                    game.deduction_opportunity(1)
                    ui.insert(result)

            # Game over
            ui.set_other_msg("")  # Clear other messages when game ends normally
            ui.render()
            if game.get_is_win():
                print(f"\n{Fore.GREEN}You won the game!{Fore.RESET} The word was '{current_word}'.\n")
            elif invalid_input_count < max_invalid_attempts:  # Only show this if not lost due to invalid inputs
                print(f"\n{Fore.RED}You lost the game.{Fore.RESET} The word was '{current_word}'.\n")
