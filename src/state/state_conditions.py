from src.state.state import GeneralGameState


class Conditions(GeneralGameState):
    """queries current game_state"""

    def in_criteria(self, *args):
        """check is current criteria is within a given list"""
        for arg in args:
            if self.criteria == arg:
                return True
        return False

    def in_mode(self, *args):
        """check if current bet-mode mates a given list"""
        for arg in args:
            if self.bet_mode == arg:
                return True
        return False

    def is_wincap(self):
        """checks if current base game + free game wins are >= max-win"""
        if self.running_bet_win >= self.config.win_cap:
            return True
        return False

    def is_in_game_type(self, *args):
        """check current game_type against possible list"""
        for arg in args:
            if self.game_type == arg:
                return True
        return False

    def get_wincap_triggered(self) -> bool:
        """Break out of spin progress if max-win is triggered."""
        if self.wincap_triggered:
            return True
        return False
