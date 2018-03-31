import time
import numpy as np

from process import PlayerProcess

from game.ww import BoardState
from game.ww import MOVES
from game.ww import WARNINGS

from game_abc import GameABC


class Game(GameABC):
    def __init__(self, config_str):
        self.config_str = config_str

        map_index_str, seed_str = self.config_str.split(';')
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
        return [self.size,
                self.units_per_player]

    def is_active(self):
        return any(self.board_state.active_players)

    def current_player(self):
        return self.board_state.current_player_id

    def turn_inputs(self, player):
        return [self.board_state.turn_input()]

    def validate_output(self, stdout_stream):
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
        self.board_state = self.board_state.next_board_state(action_str)
        self.turn += 1
        if self.turn == 400:
            # Deactivate remaining players
            self.board_state.active_players = [False, False]

    def score_game(self):
        return [self.board_state.scores[i^self.board_state.current_player_id] for i in range(2)]

    def print_game(self):
        pass
