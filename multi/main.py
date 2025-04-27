from game.game_state import GameState
from game.game_logic import GameLogic
from ui.game_ui import GameUI

def main():
    game_state = GameState()
    game_ui = GameUI()
    game_logic = GameLogic(game_state, game_ui)
    
    game_ui.set_game_logic(game_logic)
    game_ui.setup_ui()
    game_ui.root.mainloop()

if __name__ == "__main__":
    main()