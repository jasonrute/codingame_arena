import random

###################
# System Settings #
###################

# Set seed for randomness
random.seed(1)


#############
# Constants #
#############

# Game constants
DIRECTIONS = {'E':(1,0),
              'SE':(1,1),
              'S':(0,1),
              'SW':(-1,1),
              'W':(-1,0),
              'NW':(-1,-1),
              'N':(0,-1),
              'NE':(1,-1)}

PUSH_DIR_2_OPTIONS = {'W':('SW', 'W', 'NW'),
                      'NW':('W', 'NW', 'N'),
                      'N':('NW', 'N', 'NE'),
                      'NE':('N', 'NE', 'E'),
                      'E':('NE', 'E', 'SE'),
                      'SE':('E', 'SE', 'S'),
                      'S':('SE', 'S', 'SW'),
                      'SW':('S', 'SW', 'W')}

MOVES = {"ACCEPT-DEFEAT", "MOVE&BUILD", "PUSH&BUILD"}

############
# Warnings #
############

WARNINGS = {"OUT OF TIME", "OUT_OF_TIME:", "Warning:"}


################
# Action class #
################

class Action:
    def __init__(self, atype, index, dir_1, dir_2):
        self.type = atype
        self.index = int(index)
        self.dir_1 = dir_1
        self.dir_2 = dir_2

    def __str__(self):
        return "{} {} {} {}".format(self.type, self.index, self.dir_1, self.dir_2)


####################
# BoardState class #
####################

def move_by(pos, direction):
    x, y = pos
    dx, dy = DIRECTIONS[direction]
    return (x+dx, y+dy)

def unit_dist(unit_1, unit_2):
    return max(abs(unit_1[0] - unit_2[0]), abs(unit_1[1] - unit_2[1]))

class BoardState:
    def __init__(self, grid, my_units, op_units, my_score=0, op_score=0, turn=0, active_players=[True, True], current_player_id=0):
        self.turn = turn
        self.active_players = active_players
        self.grid = grid
        self.player_units = [my_units, op_units]
        self.io_units = [my_units, [u if self.is_visible(u) else (-1,-1) for u in op_units]]
        self.visible_units = [my_units, [u for u in op_units if self.is_visible(u)]]
        self.legal_actions = self.my_legal_actions()
        self.scores = [my_score, op_score]
        self.current_player_id = current_player_id

    def is_visible(self, unit):
        my_units = self.player_units[0]
        return min(unit_dist(unit, u) for u in my_units) <= 1

    def next_board_state(self, action_str):
        new_grid = self.grid.copy()
        new_my_units = self.player_units[0].copy()
        new_op_units = self.player_units[1].copy()
        new_my_score = self.scores[0]
        new_op_score = self.scores[1]
        new_turn = self.turn + 1
        new_my_active = self.active_players[0]
        new_op_active = self.active_players[1]

        if action_str not in [str(a) for a in self.legal_actions]:
            # swap order and deactivate player
            new_my_active = False
            return BoardState(new_grid, new_op_units, new_my_units, my_score=new_op_score, op_score=new_my_score, turn=new_turn, active_players=[new_op_active, new_my_active], current_player_id=self.current_player_id^1)
        else:
            action = Action(*action_str.split())

        unit = new_my_units[action.index]
        first_pos = move_by(unit, action.dir_1)
        second_pos = move_by(first_pos, action.dir_2)

        if action.type == "PUSH&BUILD":
            if second_pos in new_op_units:
                # cancelled move
                pass
            else:
                op_index = new_op_units.index(first_pos)
                new_op_units[op_index] = second_pos
                new_grid[first_pos] += 1
        else: #MOVE&BUILD
            new_my_units[action.index] = first_pos
            if new_grid[first_pos] == 3:
                    new_my_score += 1
            if second_pos in new_op_units:
                # cancelled move
                pass
            else:
                new_grid[second_pos] += 1

        if new_op_active:
            # swap my_units/score and op_units/score
            return BoardState(new_grid, new_op_units, new_my_units, my_score=new_op_score, op_score=new_my_score, turn=new_turn, active_players=[new_op_active, new_my_active], current_player_id=self.current_player_id^1)
        else:
            return BoardState(new_grid, new_my_units, new_op_units, my_score=new_my_score, op_score=new_op_score, turn=new_turn, active_players=[new_my_active, new_op_active], current_player_id=self.current_player_id)

    def my_legal_actions(self):
        legal_actions = []
        for index, u in enumerate(self.player_units[0]):
            height = self.grid[u]
            for dir_1 in DIRECTIONS:
                pos_1 = move_by(u, dir_1)
                if pos_1 in self.visible_units[1]:
                    #push
                    atype = "PUSH&BUILD"
                    for dir_2 in PUSH_DIR_2_OPTIONS[dir_1]:
                        pos_2 = move_by(pos_1, dir_2)
                        if (0 <= self.grid[pos_2] <= min(3, self.grid[pos_1]+1)
                            and pos_2 not in self.visible_units[0]
                            and pos_2 not in self.visible_units[1]):
                            legal_actions.append(Action(atype, index, dir_1, dir_2))
                elif 0 <= self.grid[pos_1] <= min(3, height+1) and pos_1 not in self.visible_units[0]:
                    atype = "MOVE&BUILD"
                    for dir_2 in DIRECTIONS:
                        pos_2 = move_by(pos_1, dir_2)
                        if (pos_2 == u
                            or (0 <= self.grid[pos_2] <= 3
                                and pos_2 not in self.visible_units[0]
                                and pos_2 not in self.visible_units[1])):
                            legal_actions.append(Action(atype, index, dir_1, dir_2))

        legal_actions.sort(key=str)
        return legal_actions

    def input_grid(self):
        rows = []
        for y in range(self.grid.shape[1]-2):
            row = []
            for x in range(self.grid.shape[0]-2):
                if self.grid[x,y] == -1:
                    row.append('.')
                else:
                    row.append(str(self.grid[x,y]))
            rows.append("".join(row))
        return "\n".join(rows)

    def turn_input(self):
        lines = []
        lines.append(self.input_grid())
        for units in self.io_units:
            for u in units:
                lines.append("{} {}".format(*u))
        lines.append(str(len(self.legal_actions)))
        for a in self.legal_actions:
            lines.append(str(a))

        return "\n".join(lines)
