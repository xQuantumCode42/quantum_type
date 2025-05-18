from game.game_state import GameState
from game.game_logic import GameLogic
from ui.game_ui import GameUI

def main():
    game_state = GameState()
    game_ui = GameUI()
    game_logic = GameLogic(game_state, game_ui)

if __name__ = "__main__":
    main()