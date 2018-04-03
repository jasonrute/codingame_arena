from abc import ABCMeta, abstractmethod

class GameABC(metaclass=ABCMeta):
    @property
    @staticmethod
    @abstractmethod
    def MIN_PLAYERS():
        """
        Return the minimum number of players for the game.

        Often 2, but some games can be one player (for testing)
        :return: int
        """
        ...

    @property
    @staticmethod
    @abstractmethod
    def MAX_PLAYERS():
        """
        Return the maximum number of players for the game.

        Often 2, but some games can be up to four players (e.g. Tron)
        :return: int
        """
        ...

    @property
    @staticmethod
    @abstractmethod
    def WARNINGS():
        """
        Return a list of strings representing special debugging
        commands that the arena app will record and print.
        :return: list of strings
        """
        ...

    @staticmethod
    @abstractmethod
    def random_configuration(random_generator):
        """
        Generate a random starting configuration string.

        It could be the configuration that CodinGame uses or an your own version.
        It is allows you to reproduce the match again.  Also use the provided
        random number generator to guarantee reproducibility.

        :param random_generator: A random number generator of type Random
        :return: The configuration string
        """
        ...

    @abstractmethod
    def __init__(self, config_str):
        """
        Read in a configuration string (generated by the random_configuration
        method) and use it to construct a new playing enviroment
        (which is stored in the object instance).

        :param str config_str: The configuration string
        """
        ...

    @abstractmethod
    def init_inputs(self, player):
        """
        Return the initial inputs sent to the player.

        These are the inputs which are only sent once to each player.

        It should be one sting possibly composed of multiple lines.

        :param int player: Player number
        :return: A single string of multiple lines
        """
        ...

    @abstractmethod
    def current_player(self):
        """
        :return: The integer of the current player
        """
        ...

    @abstractmethod
    def is_active(self):
        """
        :return: A bool representing if the game is still going on.
        """
        ...

    @abstractmethod
    def turn_inputs(self, player):
        """
        Return the inputs sent to the player at the beginning of the turn.

        It should be one sting possibly composed of multiple lines.

        :param int player: Player number (should always be the same as current player)
        :return: A single string of multiple lines
        """
        ...

    @abstractmethod
    def validate_output(self, stdout_stream):
        """
        Validate the the output given by the player is of the correct form.

        The output is of the form:

           action_str, message, issue_flag

        The action_str is a cleaned form of the output.

        Also remove and return any messages attached to the players output. Each
        CG competition usually has an easter game which lets the player attach messages
        to the action output.

        Last, the issue_flag should be False if the output was bad, else True.

        :param stdout_stream: The stdout steam collected from the player
        :return: action_str, message, issue_flag
        """
        ...

    @abstractmethod
    def process_output(self, player, action_str):
        """
        Process that players output, making their move in the game and
        setting up the game state for the next player.

        :param int player: player number
        :param str action_str: the (cleaned up) action string from validate_output
        """
        ...

    @abstractmethod
    def score_game(self):
        """
        Return a list of scores of for all the players, used to determine a winner.

        :return: A list of numbers, one for each player.
        """
        ...

    @abstractmethod
    def print_game(self):
        """
        (Optional) Print a game board or some other representation of the game state.
        Only used with show_map.

        This is used in conjunction with the show map attribute.
        """
        ...
