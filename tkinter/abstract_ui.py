from abc import ABC, abstractmethod


class AbstractUI(ABC):
    @abstractmethod
    def setup_ui(self):
        """Initialize and display the UI."""
        pass

    @abstractmethod
    def set_game_logic(self, game_logic):
        """Set the game logic instance for callbacks."""
        pass

    @abstractmethod
    def update_my_progress(self, progress):
        """Update the player's text progress"""
        pass

    @abstractmethod
    def update_opponent_progress(self, progress):
        """Update the opponent's text progress"""
        pass

    @abstractmethod
    def update_score_display(self, my_score, opponent_score=None):
        """Update the opponent's text progres display."""
        pass

    @abstractmethod
    def update_timer_display(self, remaining):
        """Update the timer display"""
        pass

    @abstractmethod
    def show_countdown(self, count):
        """Show a countdown number."""
        pass

    @abstractmethod
    def hide_countdown(self):
        """Hide the countdown display"""
        pass

    @abstractmethod
    def show_result(self, winnter, my_score=None, opponent_score=None):
        """Display the game result"""
        pass

    @abstractmethod
    def load_text_file(self):
        """Prompt the user to load a text file and return its cocntent"""
        pass

    @abstractmethod
    def set_text_content(self, text):
        """Set the text content for both player and opponent displays."""
        pass

    @abstractmethod
    def show_error_highlight(self, text):
        """Display an error text in red"""
        pass

    @abstractmethod
    def bind_key_press(self, callback):
        """Bind a key press event to a callback function."""
        pass
