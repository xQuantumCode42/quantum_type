from abc import ABC, abstractmethod


class AbstractUI(ABC):
    @abstractmethod
    def update_my_progress(self, progress):
        """Update the player's text progress"""
        pass

    @abstractmethod
    def update_opponent_progress(self, progress):
        """Update the opponent's text progress"""
        pass
