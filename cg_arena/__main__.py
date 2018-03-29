import sys, getopt
from subprocess import Popen, PIPE
from threading  import Thread
from queue import Queue, Empty
import io
import itertools

from tournament import Tournament
from match import Match

"""
Use this technique to avoid blocking of my streams:
http://stackoverflow.com/a/4896288/3494621
"""

# Helper functions

def _enqueue_output(out, queue):
    """
    Wrap the output stream in a queue, which when placed in a thread,
    will to avoid blocking.
    """
    for line in iter(out.readline, ""): # loop over the out file
        queue.put(line)
    out.close()

def _convert_output_stream_to_threaded_queue(out):
    out_queue = Queue()
    t = Thread(target=_enqueue_output, args=(out, out_queue))
    t.daemon = True # thread dies with the program
    t.start()
    return out_queue

def _read_non_blocking(queue, timeout):
    """
    Enumerate all the lines currently in the stream queue without waiting for
    more to be added later.  The timeout is how long I wait for something to
    come through the buffer.  Once it does, I read without waiting.
    """
    while True:
        # read line without blocking
        try:
            yield queue.get(timeout=timeout) # or queue.get_nowait()
            timeout = 0
        except Empty:
            return # done enumerating

class Player_Process():
    """
    Keeps track of a players process including all the tricks we use to avoid
    issues with the streams blocking.
    """

    def __init__(self, program_name, options=[]):
        p = Popen(['python3', '-u', program_name] + options, # -u prevents
                                                             # buffering on
                                                             # the child's side
                  stdout=PIPE, stdin=PIPE, stderr=PIPE,
                  bufsize=1, # Prevents buffering parent's end
                  universal_newlines=True) # Streams are text instead of bytes
        self._process = p
        self._stdout_queue = _convert_output_stream_to_threaded_queue(p.stdout)
        self._stderr_queue = _convert_output_stream_to_threaded_queue(p.stderr)
        self.stdin = p.stdin

    def read_stdout(self, timeout = .1):
        return _read_non_blocking(self._stdout_queue, timeout=timeout)

    def read_stderr(self, timeout = .1):
        return _read_non_blocking(self._stderr_queue, timeout=timeout)

    def kill(self):
        self._process.kill()





################
# Print helper #
################

def print_side_by_side(stream0, stream1, col_width=80):
    for line0, line1 in itertools.zip_longest(stream0.split('\n'), stream1.split('\n')):
        if line0 == None:
            line0 = ""
        if line1 == None:
            line1 = ""
        print("{1:{0}}{2:{0}}".format(col_width, line0.strip(), line1.strip()))



########
# Main #
########

def main(argv):
    """
    Arguements: *****_arena.py bot1 [bot2] [bot3] [bot4] [-t] [-v] [-m] [-s <config>] [-2|-3|-4] [-n <number>]'
    """
    number_of_games = 10 # Defaults to 10
    time_limits = False
    verbose = False
    show_map = False # Only works if verbose and show_map are both True
    game_arity = None # If set to 2, 3, or 4 it only plays 2, 3, 4 player games
    play_single_game = False
    play_double_game = False

    try:
        opts, args = getopt.gnu_getopt(argv, "tvmn:s:d:234", [])
    except getopt.GetoptError:
        print('****_arena.py bot1 [bot2] [bot3] [bot4] [-t] [-v] [-m] [-s <config>] [-n <number>] [-2|-3|-4]')
        sys.exit(2)

    #print(argv, opts, args) # for debugging

    if len(args) > 4:
        print("Too many bots.")
        sys.exit(2)

    elif len(args) < 1:
        print("Need at least one bot.")
        print('****_arena.py bot1 [bot2] [bot3] [bot4] [-t] [-v] [-m] [-s <config>] [-n <number>] [-2|-3|-4]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-t': # Turn on time limits
            time_limits = True
        elif opt == '-v': # Show details of each turn
            verbose = True
        elif opt == '-m': # Show game map (assuming -v or -s is set)
            show_map = True
        elif opt in ('-2', '-3', '-4'): # Play <2,3,4> player games only
            n = int(opt[1])
            if len(args) > n:
                print("Too many bots for a", n, "player game.")
                sys.exit(2)
            game_arity = n
        elif opt == '-n': # Set number of games
            number_of_games = int(arg)
        elif opt == '-s': # Play a single game with a particular given .
                          # configuration.  Some other arguments are ignored.
            if play_double_game:
                print("Can't play a single and a double game.")
                sys.exit(2)
            play_single_game = True
            config_str = arg
        elif opt == '-d': # Play a double game with a particular given .
                          # configuration.  It should be called instead of
                          # -s.
            if play_single_game:
                print("Can't play a single and a double game.")
                sys.exit(2)
            elif len(set(args)) != 2:
                print("Double game only works for 2 bots right now.")
                sys.exit(2)
            play_double_game = True
            config_str = arg


    if play_single_game or play_double_game:
        player_list = args
        #if config_str.count(",") != len(player_list):
        #    print("Number of bots doesn't match configuration number.")
        #    sys.exit(2)
        verbose = True

        if play_single_game:
            try:
                # Initiallization
                match = Match(0, config_str, player_list, time_limits, verbose, show_map)

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
                    if p: p.kill()
        else: # double_game (show side by side)
            player_names = list(set(player_list))
            reverse_player_list = []
            for p in player_list:
                reverse_player_list.append(player_names[1] if p==player_names[0]
                                           else player_names[0])
            try:
                # Initiallization (don't pass show map)
                match0 = Match(0, config_str, player_list, time_limits, verbose, False)
                match1 = Match(1, config_str, reverse_player_list, time_limits, verbose, False)

                stdout_ = sys.stdout #Keep track of the previous value.

                stream0 = io.StringIO()
                sys.stdout = stream0 # capture stdout to a stream
                match0.pregame()

                stream1 = io.StringIO()
                sys.stdout = stream1 # capture stdout to a stream
                match1.pregame()

                sys.stdout = stdout_ # restore the previous stdout.
                print_side_by_side(stream0.getvalue(), stream1.getvalue())

                stream0.close()
                stream1.close()

                # Game Loop
                while match0.is_active() or match1.is_active():
                    # Play one round of each game
                    stream0 = io.StringIO()
                    sys.stdout = stream0 # capture stdout to a stream
                    if match0.is_active():
                        match0.one_turn()

                    stream1 = io.StringIO()
                    sys.stdout = stream1 # capture stdout to a stream
                    if match1.is_active():
                        match1.one_turn()

                    sys.stdout = stdout_ # restore the previous stdout.
                    print_side_by_side(stream0.getvalue(), stream1.getvalue())

                    stream0.close()
                    stream1.close()

                    if show_map:
                        stream0 = io.StringIO()
                        sys.stdout = stream0 # capture stdout to a stream
                        match0.print_board() # not implemented yet

                        stream1 = io.StringIO()
                        sys.stdout = stream1 # capture stdout to a stream
                        match0.print_board() # not implemented yet

                        sys.stdout = stdout_ # restore the previous stdout.
                        print_side_by_side(stream0.getvalue(), stream1.getvalue())

                        stream0.close()
                        stream1.close()


                # Handle end of game details
                stream0 = io.StringIO()
                sys.stdout = stream0 # capture stdout to a stream
                match0.end_of_game()

                stream1 = io.StringIO()
                sys.stdout = stream1 # capture stdout to a stream
                match1.end_of_game()

                sys.stdout = stdout_ # restore the previous stdout.
                print_side_by_side(stream0.getvalue(), stream1.getvalue())

                stream0.close()
                stream1.close()

            except:
                raise
            finally:
                # Kill all subprocesses even if a crash
                for p in match0.player_processes:
                    if p: p.kill()
                for p in match1.player_processes:
                    if p: p.kill()


    else:
        program_names = args
        t = Tournament(number_of_games, program_names, game_arity, time_limits, verbose, show_map)
        #cProfile.runctx('t.play_all_games()', None, locals())
        t.play_all_games()
        t.print_win_data()


if __name__ == "__main__":
    main(sys.argv[1:])




