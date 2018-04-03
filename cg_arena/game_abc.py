from abc import ABCMeta, abstractmethod

class GameABC(metaclass=ABCMeta):
    @property
    @staticmethod
    @abstractmethod
    def MIN_PLAYERS():
        ...

    @property
    @staticmethod
    @abstractmethod
    def MAX_PLAYERS():
        ...

    @staticmethod
    @abstractmethod
    def random_configuration(random_generator):
        ...

    @abstractmethod
    def __init__(self, config_str):
        ...

    @abstractmethod
    def init_inputs(self, player):
        ...

    @abstractmethod
    def current_player(self):
        ...

    @abstractmethod
    def is_active(self):
        ...

    @abstractmethod
    def turn_inputs(self, player):
        ...

    @abstractmethod
    def process_output(self, player, action_str):
        ...

    @abstractmethod
    def score_game(self):
        pass

    @abstractmethod
    def print_game(self):
        pass
