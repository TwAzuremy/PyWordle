import argparse
import colorama
import config.config as config

from game.game_controller import GameController

colorama.init(autoreset=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    config.DEBUG = args.debug

    game = GameController()
    game.run()
