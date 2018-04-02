"""
The main application.
"""


import sys
import getopt
import io
import itertools

from tournament import Tournament
from match import Match


def print_side_by_side(stream0, stream1, col_width=80):
    """
    Prints two streams side by side.

    Used to print two games next to each other.  The streams are captured stdout
    streams.

    :param stream0: STDOUT stream 0
    :param stream1: STDOUT stream 1
    :param int col_width: column width
    """
    for line0, line1 in itertools.zip_longest(stream0.split('\n'),
                                              stream1.split('\n')):
        if line0 is None:
            line0 = ""
        if line1 is None:
            line1 = ""
        print("{1:{0}}{2:{0}}".format(col_width, line0.strip(), line1.strip()))


class Arena:
    """
    Runs the application.
    """

    def __init__(self, argv):
        """
        Parse the arguments to the application and store the settings.

        We assume the arguments to the app follow this pattern:

        bot1 [bot2] [bot3] [bot4] [-t] [-v] [-m] [-s <config>] [-2|-3|-4] [-n <number>]

        :param argv: The command line arguments passed to the application as given
                     by sys.argv
        :returns: The initialized areana object
        """

        # parameters (set to defaults)
        self.number_of_games = 10  # Defaults to 10
        self.time_limits = False
        self.verbose = False
        self.show_map = False  # Only works if verbose and show_map are both True
        self.game_arity = None  # If set to 2, 3, or 4 it only plays 2, 3, 4 player games
        self.single_game = False
        self.double_game = False
        self.config_str = None
        self.player_list = []


        try:
            opts, args = getopt.gnu_getopt(argv[1:], "tvmn:s:d:234", [])
        except getopt.GetoptError:
            print(argv[0], 'bot1 [bot2] [bot3] [bot4] [-t] [-v] [-m] [-s <config>] [-n <number>] [-2|-3|-4]')
            sys.exit(2)

        if len(args) > 4:
            print("Too many bots.")
            sys.exit(2)

        elif len(args) < 1:
            print("Need at least one bot.")
            print(argv[0], 'bot1 [bot2] [bot3] [bot4] [-t] [-v] [-m] [-s <config>] [-n <number>] [-2|-3|-4]')
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-t':  # Turn on time limits
                self.time_limits = True
            elif opt == '-v':  # Show details of each turn
                self.verbose = True
            elif opt == '-m':  # Show game map (assuming -v or -s is set)
                self.show_map = True
            elif opt in ('-2', '-3', '-4'):  # Play <2,3,4> player games only
                n = int(opt[1])
                if len(args) > n:
                    print("Too many bots for a", n, "player game.")
                    sys.exit(2)
                self.game_arity = n
            elif opt == '-n':  # Set number of games
                self.number_of_games = int(arg)
            elif opt == '-s': # Play a single game with a particular given
                              # configuration.  Some other arguments are ignored.
                if self.double_game:
                    print("Can't play a single and a double game.")
                    sys.exit(2)
                self.single_game = True
                self.config_str = arg
            elif opt == '-d':  # Play a double game with a particular given .
                               # configuration.  It should be called instead of
                               # -s.
                if self.single_game:
                    print("Can't play a single and a double game.")
                    sys.exit(2)
                elif len(set(args)) != 2:
                    print("Double game only works for 2 bots right now.")
                    sys.exit(2)
                self.double_game = True
                self.config_str = arg

        self.player_list = args

    def run(self):
        """Run the application according to the provided arguments."""

        if self.single_game or self.double_game:
            self.verbose = True

            if self.single_game:
                self.play_single_game()

            else:  # double_game (show side by side)
                self.play_double_game()

        else:
            self.play_tournament()

    def play_single_game(self):
        try:
            # Initialization
            match = Match(0, self.config_str, self.player_list, self.time_limits, self.verbose, self.show_map)

            match.pregame()
            # Game Loop
            while match.is_active():
                # Play one round of the game
                match.one_turn()

            # Handle end of game details
            match.end_of_game()

        except:
            raise
        finally:
            # Kill all subprocesses even if a crash
            for p in match.player_processes:
                if p:
                    p.kill()

    def play_double_game(self):
        player_names = list(set(self.player_list))
        reverse_player_list = []
        for p in self.player_list:
            reverse_player_list.append(player_names[1] if p == player_names[0]
                                       else player_names[0])
        try:
            # Initialization (don't pass show map)
            match0 = Match(0, self.config_str, self.player_list, self.time_limits, self.verbose, False)
            match1 = Match(1, self.config_str, reverse_player_list, self.time_limits, self.verbose, False)

            stdout_ = sys.stdout  # Keep track of the previous value.

            stream0 = io.StringIO()
            sys.stdout = stream0  # capture stdout to a stream
            match0.pregame()

            stream1 = io.StringIO()
            sys.stdout = stream1  # capture stdout to a stream
            match1.pregame()

            sys.stdout = stdout_  # restore the previous stdout.
            print_side_by_side(stream0.getvalue(), stream1.getvalue())

            stream0.close()
            stream1.close()

            # Game Loop
            while match0.is_active() or match1.is_active():
                # Play one round of each game
                stream0 = io.StringIO()
                sys.stdout = stream0  # capture stdout to a stream
                if match0.is_active():
                    match0.one_turn()

                stream1 = io.StringIO()
                sys.stdout = stream1  # capture stdout to a stream
                if match1.is_active():
                    match1.one_turn()

                sys.stdout = stdout_  # restore the previous stdout.
                print_side_by_side(stream0.getvalue(), stream1.getvalue())

                stream0.close()
                stream1.close()

                if self.show_map:
                    stream0 = io.StringIO()
                    sys.stdout = stream0  # capture stdout to a stream
                    match0.print_board()  # not implemented yet

                    stream1 = io.StringIO()
                    sys.stdout = stream1  # capture stdout to a stream
                    match0.print_board()  # not implemented yet

                    sys.stdout = stdout_  # restore the previous stdout.
                    print_side_by_side(stream0.getvalue(), stream1.getvalue())

                    stream0.close()
                    stream1.close()


            # Handle end of game details
            stream0 = io.StringIO()
            sys.stdout = stream0  # capture stdout to a stream
            match0.end_of_game()

            stream1 = io.StringIO()
            sys.stdout = stream1  # capture stdout to a stream
            match1.end_of_game()

            sys.stdout = stdout_  # restore the previous stdout.
            print_side_by_side(stream0.getvalue(), stream1.getvalue())

            stream0.close()
            stream1.close()

        except:
            raise
        finally:
            # Kill all subprocesses even if a crash
            for p in match0.player_processes:
                if p:
                    p.kill()
            for p in match1.player_processes:
                if p:
                    p.kill()

    def play_tournament(self):
        t = Tournament(self.number_of_games, self.player_list, self.game_arity, self.time_limits, self.verbose, self.show_map)
        t.play_all_games()
        t.print_win_data()



