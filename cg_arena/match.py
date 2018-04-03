import time

from process import PlayerProcess
from game import Game
# TODO: Handle these

from game.ww import WARNINGS




##############
# Game class #
##############

class Match():
    """
    Stores the current state of the game.
    """

    def __init__(self, id_number, config_str, player_program_list, time_limits, verbose, show_map):
        """
        Initializes all game data
        """

        #
        # Counters/Timers
        #
        self.turn = -1 # Counter will update at beginning of round.
        self.start_time = time.perf_counter()
        self.total_time = time.perf_counter()

        #
        # Fixed information
        #

        self.id_number = id_number
        self.number_of_starting_players = len(player_program_list)
        self.player_program_list = player_program_list
        max_name_len = max([len(name) for name in player_program_list])
        self.padded_names = [name.ljust(max_name_len) for name in player_program_list]
        self.config_str = config_str
        self.time_limits = time_limits
        self.verbose = verbose
        self.show_map = show_map

        #
        # Start the programs running as subprocesses
        #
        self.player_processes = []
        for program_name in player_program_list:

            options = []
            if not self.time_limits:
                options = ['--no-time-limit']
            self.player_processes.append(PlayerProcess(program_name, options))

        #
        # Use config string to determine initial configuration/starting positions
        #

        # Create game
        self.game = Game(config_str)

        # # TODO: BEGIN Game(config_str)
        # # Specific to Wonder Women
        #
        # map_index_str, seed_str = self.config_str.split(';')
        # map_index = int(map_index_str.split('=')[1])
        # seed = int(seed_str.split("=")[1])
        # np.random.seed(seed)
        #
        # self.units_per_player = 2
        #
        # # grid
        # if map_index == 0:
        #     self.size = 5
        #     grid = np.zeros((7, 7),dtype=int)
        #     grid[5,:] = -1
        #     grid[6,:] = -1
        #     grid[:,5] = -1
        #     grid[:,6] = -1
        # elif map_index == 1:
        #     self.size = 7
        #     grid = np.array([[-1,-1,-1, 0,-1,-1,-1,-1,-1],
        #                      [-1,-1, 0, 0, 0,-1,-1,-1,-1],
        #                      [-1, 0, 0, 0, 0, 0,-1,-1,-1],
        #                      [ 0, 0, 0, 0, 0, 0, 0,-1,-1],
        #                      [-1, 0, 0, 0, 0, 0,-1,-1,-1],
        #                      [-1,-1, 0, 0, 0,-1,-1,-1,-1],
        #                      [-1,-1,-1, 0,-1,-1,-1,-1,-1],
        #                      [-1,-1,-1,-1,-1,-1,-1,-1,-1],
        #                      [-1,-1,-1,-1,-1,-1,-1,-1,-1]],dtype=int)
        # elif map_index == 2:
        #     self.size = 6
        #     grid = np.zeros((8, 8),dtype=int)
        #     grid[6,:] = -1
        #     grid[7,:] = -1
        #     grid[:,6] = -1
        #     grid[:,7] = -1
        #     # remove one element
        #     x = np.random.randint(3)
        #     y = np.random.randint(6)
        #     grid[x,y] = -1
        #     grid[6-x-1,y] = -1
        #     # flip remining bits with one percent probability
        #     prob = np.random.randint(0, 70, size=(8,8))
        #     remove = (prob == 0) | (prob[[5,4,3,2,1,0,7,6],:] == 0)
        #     grid[remove] = -1
        #
        # # player locations
        # x, y = np.indices(grid.shape)
        # x = x[grid == 0]
        # y = y[grid == 0]
        # indx = np.random.choice(np.arange(x.size), 4, replace=False)
        # player_units = list(zip(x[indx], y[indx]))
        #
        # #
        # # Information which changes each turn specific the the game
        # #
        #
        # # Specific to Wonder Women
        #
        # self.board_state = BoardState(grid, player_units[:2], player_units[2:], my_score=0, op_score=0, turn=0, active_players=[True, True])
        #
        # # TODO: END Game(config_str)
        #
        # General information for all games
        #
        self.current_player = 0
        self.loss_order = [] # list of players as they lose
        self.issue_logs = [None for p in player_program_list]
        self.warnings = [[] for p in player_program_list]
        self.sum_times = [0 for p in player_program_list]
        self.max_times = [0 for p in player_program_list]
        self.player_turns = [0 for p in player_program_list]

    def kill_player(self, player):
        # Close the process and remove from process list
        self.player_processes[player].kill()
        self.player_processes[player] = None

        # TODO: Record loss order differently
        # Mark player as lost
        self.loss_order.append(player)

    def send_init_inputs_to_player(self):
        # To avoid timing issues, I will send the information to each player seperately.
        # It will be basically the same information.

        try:
            current_player_stdin = self.player_processes[self.current_player].stdin

            for line in self.game.init_inputs(self.current_player):
                print(line, file=current_player_stdin)

            # # TODO: BEGIN Game.init_inputs(player)
            # # Specific to WonderWomen
            # print(self.size, file=current_player_stdin)
            # print(self.units_per_player, file=current_player_stdin)
            # # TODO: END Game.init_inputs(player)

            return time.perf_counter(), False # no errors

        except BrokenPipeError:
            print("Broken Pipe Error")
            return time.perf_counter(), True # errors (Program likely crashed)

    def pregame(self):
        print("==========================")
        print("Game:", self.id_number)
        print("Configuration:", self.config_str)
        print("Players:")
        for player, player_name in enumerate(self.player_program_list):
            print(player, ":", player_name)

            self.current_player = player
            input_time, input_flag = self.send_init_inputs_to_player()
            # Won't bother with the input flag now.  We will wait for it to crash on the first turn

    def is_active(self):
        # TODO: get rid of this Match.is_active  Replace with next line
        return self.game.is_active()

        # # TODO: START Game.is_active()
        # # Special to Wonder Women
        #
        # return any(self.board_state.active_players)
        # # TODO: END Game.is_active()

    def send_inputs_to_player(self):
        try:
            current_player_stdin = self.player_processes[self.current_player].stdin

            for line in self.game.turn_inputs(self.current_player):
                print(line, file=current_player_stdin)

            # # TODO: START Game.turn_inputs(player)
            # # Specific to WonderWomen
            #
            # print(self.board_state.turn_input(), file=current_player_stdin)
            # # TODO: END Game.turn_inputs(player)

            return time.perf_counter(), False # no errors

        except BrokenPipeError:
            print("Broken Pipe Error")
            return time.perf_counter(), True # errors (Program likely crashed)

    def read_player_streams(self, timeout = 0.1, expected_stdout_size = 1):
        p = self.player_processes[self.current_player]

        # read from stdout first since that means they are done with their turn
        stdout_stream = list(p.read_stdout(timeout = timeout))
        if len(stdout_stream) < expected_stdout_size:
            stdout_stream += list(p.read_stdout(timeout = 0.01))
        output_time = time.perf_counter()
        # read stderr next with no timeout since it should all be put into
        # the stream by now
        stderr_stream = list(p.read_stderr(timeout = 0.01))

        return output_time, stdout_stream, stderr_stream

    def validate_player_output(self, stdout_stream):
        return self.game.validate_output(stdout_stream)

        # # TODO: BEGIN
        # issue_flag = False # used to flag undesired behavior
        # message = ""
        # action_str = None
        #
        # # Much of this method is specific to Wonder Women
        # if not stdout_stream:
        #     message += "did not provide any output. (CRASHED?)"
        #     issue_flag = True
        #
        # else:
        #     raw_move = stdout_stream[0].rstrip()
        #     move = raw_move.split()
        #     if not move:
        #         message += "played " + raw_move + " which is not a valid move."
        #         issue_flag = True
        #     elif move[0] not in MOVES:
        #         message += "played " + raw_move + " which is not a valid move."
        #         issue_flag = True
        #     elif move[0] == "ACCEPT-DEFEAT":
        #         action_str = "ACCEPT-DEFEAT"
        #     else:
        #         action_str = " ".join(move[:4])
        #         if action_str not in [str(a) for a in self.board_state.legal_actions]:
        #             message += "played " + raw_move + " which is not in list of legal moves."
        #             issue_flag = True
        #             action_str = None
        #
        # return action_str, message, issue_flag
        # TODO: END

    def process_players_errors(self, stderr_stream):
        warning_set = set() # A set to avoid duplicates
        for line in stderr_stream:
            line = line.rstrip()
            if line and (line in WARNINGS or line.split()[0] in WARNINGS):
                warning_set.add((self.turn, line))
        self.warnings[self.current_player].extend(warning_set)

    def process_players_output(self, action_str):
        # TODO: get rid of this method (replace with next line)
        return self.game.process_output(self.current_player, action_str)

        # # TODO: BEGIN Game.process_output(action_str)
        # # This method is specific to Wonder Women
        # self.board_state = self.board_state.next_board_state(action_str)
        # if self.turn == 400:
        #     # Deactivate remaining players
        #     self.board_state.active_players = [False, False]
        # # TODO: END Game.process_output(action_str)

    def record_times(self, input_time, output_time):
        player = self.current_player
        if self.player_turns[player]: # skip first turn
            turn_time = output_time - input_time
            self.sum_times[player] += turn_time
            if self.max_times[player] < turn_time:
                self.max_times[player] = turn_time

        self.player_turns[player] += 1

    def print_board(self):
        # TODO: get rid of this method (replace with next line)
        self.game.print_board()

        # TODO: BEGIN Game.print_board()
        # specific to Wonder Women

        print("Print board not implemented yet")
        # TODO: END Game.print_board()

    def print_turn_data(self, stdout_stream, stderr_stream, message, issue_flag, input_time, output_time):
        player_name = self.player_program_list[self.current_player]
        print("--------------------------")
        print("Turn", self.turn, "(Player {})".format(self.current_player), player_name)

        print("Standard Error Stream:")
        for line in stderr_stream:
            print(">", line, end="")
        print("Standard Output Stream:")
        for line in stdout_stream:
            print(">", line, end="")
        print("Game Information:")
        print(">", player_name, message)
        print("Turn time:", output_time - input_time, "sec")
        if self.show_map: self.print_board()  # not implemented yet

    def print_error_report(self, player):
        turn, stdout_stream, stderr_stream, \
              message, input_flag, output_flag = self.issue_logs[player]
        player_name = self.player_program_list[player]
        print("    Error on turn", self.turn)

        print("    Standard Error Stream:")
        for line in stderr_stream:
            print("    >", line, end="")
        print("    Standard Output Stream:")
        for line in stdout_stream:
            print("    >", line, end="")
        print("    Game Information:")
        print("    >", player_name, message)

    def one_turn(self):
        """
        Perform one turn in the game (for each player) from sending input to reading the streams
        """

        #
        # Mark time that the previous move took
        #

        self.start_time = time.perf_counter()
        self.turn += 1

        #
        # Send inputs and read outputs
        #
        self.current_player = self.game.current_player()
        # TODO: remove commented out text:
        #self.current_player = self.board_state.current_player_id

        input_time, input_flag = self.send_inputs_to_player()
        output_time, stdout_stream, stderr_stream = self.read_player_streams(timeout = 2, expected_stdout_size = 1)
        moves, message, output_flag = self.validate_player_output(stdout_stream)
        warnings = self.process_players_errors(stderr_stream)
        self.record_times(input_time, output_time)
        if input_flag or output_flag:
            self.kill_player(self.current_player)
            self.issue_logs[self.current_player] = (self.turn, stdout_stream,
                                                     stderr_stream, message,
                                                     input_flag, output_flag)
        #
        # Process outputs
        #
        if self.is_active():
            self.process_players_output(moves)

        if self.verbose:
            self.print_turn_data(stdout_stream, stderr_stream, message, output_flag, input_time, output_time)

    def remaining_players_in_order(self):
        # TODO: Eventually remove this, handle ties and deactivated players better

        # ties are (not so) rare, so I can worry about that later

        # TODO: BEGIN
        #active_players = [i for i in range(self.number_of_starting_players) if self.player_processes[i]]
        #active_players.sort(key=lambda i: self.board_state.scores[i^self.board_state.current_player_id])
        # TODO: END

        return sorted(range(self.number_of_starting_players), key=lambda p: self.game.score_game()[p])

    def end_of_game(self):

        # Kill remaining players
        for i in self.remaining_players_in_order():
            self.kill_player(i)

        print("--------------------------")
        print("Game", self.id_number, "results:")
        for place, player in enumerate(reversed(self.loss_order)):
            if self.player_turns[player]:
                ave_time = self.sum_times[player]/self.player_turns[player]
            else:
                ave_time = 0.0
            max_time = self.max_times[player]
            print(place + 1, ":",
                "(Player {})".format(player),
                self.padded_names[player],
                "   [ave: {:.5f} sec, max: {:.5f} sec]".format(ave_time, max_time))
            if self.issue_logs[player]:
                self.print_error_report(player)
            if self.warnings[player]:
                for turn, message in self.warnings[player]:
                    print("    Warning on turn", turn, ":", message)


        print("Total time:", time.perf_counter() - self.total_time, "sec")