"""
An implementation of engine for the Wondev Women competition on CodinGame.

This can be modified to implement any CodinGame competition.
"""

import numpy as np

from game.ww import BoardState
from game.ww import MOVES
from game.ww import WARNINGS

from game_abc import GameABC


class Game(GameABC):

    MIN_PLAYERS = 1  # One player is allowed for debugging purposes and end game analysis
    MAX_PLAYERS = 2  # WW played with 2 players
    WARNINGS = WARNINGS  # Special debug codes

    @staticmethod
    def random_configuration(rng):
        """
        Generate a random starting configuration string.

        It could be the configuration that CodinGame uses or an your own version.
        It is allows you to reproduce the match again.  Also use the provided
        random number generator to guarantee reproducibility.

        :param random_generator: A random number generator of type Random
        :return: The configuration string
        """

        # This is specific to Wonder Women
        map_index = rng.randrange(3)
        seed = rng.randrange(2**32)
        config_str = "mapIndex={};seed={}".format(map_index, seed)

        return config_str

    def __init__(self, config_str):
        """
        Read in a configuration string (generated by the random_configuration
        method) and use it to construct a new playing enviroment
        (which is stored in the object instance).

        :param str config_str: The configuration string
        """

        self._config_str = config_str

        map_index_str, seed_str = self._config_str.split(';')
        map_index = int(map_index_str.split('=')[1])
        seed = int(seed_str.split("=")[1])
        np.random.seed(seed)

        self.units_per_player = 2

        # grid
        if map_index == 0:
            self.size = 5
            grid = np.zeros((7, 7),dtype=int)
            grid[5,:] = -1
            grid[6,:] = -1
            grid[:,5] = -1
            grid[:,6] = -1
        elif map_index == 1:
            self.size = 7
            grid = np.array([[-1,-1,-1, 0,-1,-1,-1,-1,-1],
                             [-1,-1, 0, 0, 0,-1,-1,-1,-1],
                             [-1, 0, 0, 0, 0, 0,-1,-1,-1],
                             [ 0, 0, 0, 0, 0, 0, 0,-1,-1],
                             [-1, 0, 0, 0, 0, 0,-1,-1,-1],
                             [-1,-1, 0, 0, 0,-1,-1,-1,-1],
                             [-1,-1,-1, 0,-1,-1,-1,-1,-1],
                             [-1,-1,-1,-1,-1,-1,-1,-1,-1],
                             [-1,-1,-1,-1,-1,-1,-1,-1,-1]],dtype=int)
        elif map_index == 2:
            self.size = 6
            grid = np.zeros((8, 8),dtype=int)
            grid[6,:] = -1
            grid[7,:] = -1
            grid[:,6] = -1
            grid[:,7] = -1
            # remove one element
            x = np.random.randint(3)
            y = np.random.randint(6)
            grid[x,y] = -1
            grid[6-x-1,y] = -1
            # flip remining bits with one percent probability
            prob = np.random.randint(0, 70, size=(8,8))
            remove = (prob == 0) | (prob[[5,4,3,2,1,0,7,6],:] == 0)
            grid[remove] = -1

        # player locations
        x, y = np.indices(grid.shape)
        x = x[grid == 0]
        y = y[grid == 0]
        indx = np.random.choice(np.arange(x.size), 4, replace=False)
        player_units = list(zip(x[indx], y[indx]))

        #
        # Information which changes each turn specific the the game
        #

        self.turn = 0

        self.board_state = BoardState(grid, player_units[:2], player_units[2:], my_score=0, op_score=0, turn=0, active_players=[True, True])

    def init_inputs(self, player):
        """
        Return the initial inputs sent to the player.

        These are the inputs which are only sent once to each player.

        It should be one sting possibly composed of multiple lines.

        :param int player: Player number
        :return: A single string of multiple lines
        """

        return [self.size,
                self.units_per_player]

    def is_active(self):
        """
        :return: A bool representing if the game is still going on.
        """
        return any(self.board_state.active_players)

    def current_player(self):
        """
        :return: The integer of the current player
        """
        return self.board_state.current_player_id

    def turn_inputs(self, player):
        """
        Return the inputs sent to the player at the beginning of the turn.

        It should be one sting possibly composed of multiple lines.

        :param int player: Player number (should always be the same as current player)
        :return: A single string of multiple lines
        """
        return [self.board_state.turn_input()]

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
        # TODO: move some of the boilerplate back to Match.validate_output

        issue_flag = False # used to flag undesired behavior
        message = ""
        action_str = None

        # Much of this method is specific to Wonder Women
        if not stdout_stream:
            message += "did not provide any output. (CRASHED?)"
            issue_flag = True

        else:
            raw_move = stdout_stream[0].rstrip()
            move = raw_move.split()
            if not move:
                message += "played " + raw_move + " which is not a valid move."
                issue_flag = True
            elif move[0] not in MOVES:
                message += "played " + raw_move + " which is not a valid move."
                issue_flag = True
            elif move[0] == "ACCEPT-DEFEAT":
                action_str = "ACCEPT-DEFEAT"
            else:
                action_str = " ".join(move[:4])
                if action_str not in [str(a) for a in self.board_state.legal_actions]:
                    message += "played " + raw_move + " which is not in list of legal moves."
                    issue_flag = True
                    action_str = None

        return action_str, message, issue_flag

    def process_output(self, player, action_str):
        """
        Process that players output, making their move in the game and
        setting up the game state for the next player.

        :param int player: player number
        :param str action_str: the (cleaned up) action string from validate_output
        """
        self.board_state = self.board_state.next_board_state(action_str)
        self.turn += 1
        if self.turn == 400:
            # Deactivate remaining players
            self.board_state.active_players = [False, False]

    def score_game(self):
        """
        Return a list of scores of for all the players, used to determine a winner.

        :return: A list of numbers, one for each player.
        """
        return [self.board_state.scores[i^self.board_state.current_player_id] for i in range(2)]

    def print_game(self):
        """
        (Optional) Print a game board or some other representation of the game state.
        Only used with show_map.

        This is used in conjunction with the show map attribute.
        """
        pass
