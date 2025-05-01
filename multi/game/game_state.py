import queue
import time

class GameState:
    def __init__(self):
        self.is_host = False
        self.is_single_player = True
        self.network = None
        self.queue = queue.Queue()
        self.game_started = False
        self.start_time = 0
        self.my_progress = 0
        self.my_score = 0
        self.opponent_progress = 0
        self.opponent_score = 0
        self.text_content = ""
        
        # Add attributes for text chunking
        self.text_chunks = []
        self.total_chunks = 0
        self.received_chunks = 0