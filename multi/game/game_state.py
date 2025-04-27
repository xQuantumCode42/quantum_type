import queue
import time

class GameState:
    def __init__(self):
        self.is_host = None
        self.is_single_player = False
        self.network = None
        self.queue = queue.Queue()
        self.game_started = False
        self.start_time = None
        self.my_progress = 0
        self.my_score = 0
        self.opponent_progress = 0
        self.opponent_score = 0
        self.text_content = ""