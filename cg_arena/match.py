import time

from process import PlayerProcess
from game import Game




class Match:
    """
    Stores the current state of the match including managing the player processes.
    """

    def __init__(self, id_number, config_str, player_program_list, time_limits, verbose, show_map):
        """
        Initializes all game data
        """

        #
        # Counters/Timers
        #
        self.turn = -1  # Counter will update at beginning of round.
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

        #
        # General information for all games
        #
        self.current_player = 0
        self.loss_order = []  # list of players as they lose
        self.issue_logs = [None for _ in player_program_list]
        self.warnings = [[] for _ in player_program_list]
        self.sum_times = [0 for _ in player_program_list]
        self.max_times = [0 for _ in player_program_list]
        self.player_turns = [0 for _ in player_program_list]

    def kill_player(self, player):
        """
        Kill the player's process and record loss.
        :param int player:
        :return:
        """
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

            return time.perf_counter(), False  # no errors

        except BrokenPipeError:
            print("Broken Pipe Error")
            return time.perf_counter(), True  # errors (Program likely crashed)

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
        """Check if the game is still active."""

        return self.game.is_active()

    def send_inputs_to_player(self):
        """
        Send information to the player processes at the start of the turn.

        :return: time that the input was sent (needed to measure response time)
        :return: a flag representing if there was a Broken Pipe Error
                 (which likely means the processes crashed)
        """

        try:
            current_player_stdin = self.player_processes[self.current_player].stdin

            for line in self.game.turn_inputs(self.current_player):
                print(line, file=current_player_stdin)

            return time.perf_counter(), False  # no errors

        except BrokenPipeError:
            print("Broken Pipe Error")
            return time.perf_counter(), True  # errors (Program likely crashed)

    def read_player_streams(self, timeout=0.1, expected_stdout_size=1):
        """
        Get the actions from the player processes stdin (and stuff from stderr)

        :param timeout:
        :param expected_stdout_size:
        :return: time that the output was collected
        :return: stdout stream
        :return: stderr stream
        """

        p = self.player_processes[self.current_player]

        # read from stdout first since that means they are done with their turn
        stdout_stream = list(p.read_stdout(timeout=timeout))
        if len(stdout_stream) < expected_stdout_size:
            stdout_stream += list(p.read_stdout(timeout=0.01))
        output_time = time.perf_counter()
        # read stderr next with no timeout since it should all be put into
        # the stream by now
        stderr_stream = list(p.read_stderr(timeout=0.01))

        return output_time, stdout_stream, stderr_stream

    def validate_player_output(self, stdout_stream):
        """
        Determine if player output was good.

        :param stdout_stream: The stdout steam collected form the player
        :return: action_str, message, issue_flag
        """
        return self.game.validate_output(stdout_stream)

    def process_players_errors(self, stderr_stream):
        """
        Process any errors from the players.

        I particular, the stderr output can include debugging code, so I used
        the Game.WARNINGS list to notes special errors that I want to print.

        :param stderr_stream: The error stream from the player process.
        """

        warning_set = set()  # A set to avoid duplicates
        for line in stderr_stream:
            line = line.rstrip()
            if line and (line in Game.WARNINGS or line.split()[0] in Game.WARNINGS):
                warning_set.add((self.turn, line))
        self.warnings[self.current_player].extend(warning_set)

    def process_players_output(self, action_str):
        """
        Process the actions printed by the player.

        :param action_str: The stream of actions printed by the player.
        """

        return self.game.process_output(self.current_player, action_str)

    def record_times(self, input_time, output_time):
        player = self.current_player
        if self.player_turns[player]:  # skip first turn
            turn_time = output_time - input_time
            self.sum_times[player] += turn_time
            if self.max_times[player] < turn_time:
                self.max_times[player] = turn_time

        self.player_turns[player] += 1

    def print_board(self):
        """
        Print the game board.  (Used with show_map attribute.)
        """

        self.game.print_game()

    def print_turn_data(self, stdout_stream, stderr_stream, message, issue_flag, input_time, output_time):
        """
        Print summary information about the turn.

        :param stdout_stream:
        :param stderr_stream:
        :param str message:
        :param bool issue_flag:
        :param input_time:
        :param output_time:
        :return:
        """

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
        if self.show_map:
            self.print_board()

    def print_error_report(self, player):
        """
        Print an error report (for when the process crashes).
        :param int player: The player number
        """

        turn, stdout_stream, stderr_stream, message, input_flag, output_flag = self.issue_logs[player]
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
        Perform one turn in the game (for each player).

        Send info to process, read info from process, validate and process moves
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

        input_time, input_flag = self.send_inputs_to_player()
        output_time, stdout_stream, stderr_stream = self.read_player_streams(timeout=2, expected_stdout_size=1)
        moves, message, output_flag = self.validate_player_output(stdout_stream)
        self.process_players_errors(stderr_stream)
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
        """
        Returns a list of the remaining players in order of score to determine
        winner
        """

        return sorted(range(self.number_of_starting_players), key=lambda p: self.game.score_game()[p])

    def end_of_game(self):
        """
        Stuff to handle at the end of the game like recording the winners and
        killing all the player processes.
        """

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
