import random
import time

from match import Match
from game import Game


class Tournament:
    """
    Manages a tournament of multiple games.
    """
    def __init__(self, number_of_games, program_names, game_arity, time_limits, verbose, show_map):
        """
        Initialize

        :param int number_of_games: Number of games in the tournament
        :param program_names: List of python scripts to run
        :param int game_arity: Maximum number of players per match
        :param bool time_limits: Use time limits
        :param bool verbose: Print information about every move
        :param bool show_map: Print the game board
        :return:
        """

        self.number_of_games = number_of_games
        self.program_names = program_names
        self.num_bots = len(self.program_names)
        self.game_arity = game_arity
        self.time_limits = time_limits
        self.verbose = verbose
        self.show_map = show_map

        self.results = []
        self.player_lists = []
        self.wins = {p: 0 for p in program_names}
        self.placements = {(p, a, i): 0 for p in program_names for a in (2, 3, 4) for i in range(a)}
        self.totals_by_arity = {a: 0 for a in (2, 3, 4)}
        self.diff_results = []
        self.diff_totals_by_arity = {a: 0 for a in (2, 3, 4)}
        self.diff_wins = {p: 0 for p in program_names}
        self.diff_placements = {(p, a, i): 0 for p in program_names for a in (2, 3, 4) for i in range(a)}
        self.games_with_errors = {p: [] for p in program_names}
        self.games_with_warnings = {p: [] for p in program_names}
        self.games_played = 0
        self.games_to_look_at = []

        self.start_time = time.perf_counter()

        self.player_order_rng = random.Random(0)
        self.config_str_rng = random.Random(0)

    def generate_random_configurations(self):
        """
        Generators a tuple specifying which players are playing in what order.

        :return: a tuple with the player
        """

        if self.game_arity:
            game_arity = self.game_arity
        else:
            game_arity = min(2, Game.MIN_PLAYERS)  # this is just a two player game

        num_bots = self.num_bots
        player_order = None

        # get random configuration so that not all one player
        while player_order is None or all(i == player_order[0] for i in player_order):
            player_order = [random.randrange(num_bots) for _ in range(game_arity)]

        # generate configuration string
        config_str = Game.random_configuration(self.config_str_rng)

        # rotate players to give some semplance of symmetry (esp in 2 bot case)
        random_configs = []
        for i in range(num_bots):
            player_list = [self.program_names[(j+i) % num_bots] for j in player_order]
            random_configs.append((player_list, config_str))

        return random_configs

    def play_game(self, id_number, player_list, config_str):
        """
        Plays the match from beginning to end, recording the results.

        :param id_number:
        :param player_list:
        :param config_str:
        """
        match = None
        try:
            # Initialization
            match = Match(id_number, config_str, player_list, self.time_limits, self.verbose, self.show_map)

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
            if match is not None:
                for p in match.player_processes:
                    if p:
                        p.kill()

        results = tuple(reversed(match.loss_order))
        arity = len(player_list)
        self.results.append(results)
        self.player_lists.append(player_list)
        self.totals_by_arity[arity] += 1
        self.wins[player_list[results[0]]] += 1
        for place, i in enumerate(results):
            player_name = player_list[i]
            self.placements[player_name, arity, place] += 1
        for i, log in enumerate(match.issue_logs):
            player_name = player_list[i]
            if log:
                self.games_with_errors[player_name].append(match.id_number)
        for i, warning_log in enumerate(match.warnings):
            player_name = player_list[i]
            if warning_log:
                self.games_with_warnings[player_name].append(match.id_number)

    def play_all_games(self):
        """
        Play all the matches.
        """
        random_configs = []

        for i in range(self.number_of_games):
            if i % 10 == 0:
                self.print_win_data()

            if not random_configs:
                random_configs = self.generate_random_configurations()

            player_list, config_str = random_configs.pop()
            self.play_game(i, player_list, config_str)
            self.games_played += 1

            if not random_configs:
                # check if all the results of the last set are not the same
                if len(set(self.results[-self.num_bots:])) > 1:
                    self.games_to_look_at.append(tuple(range(i-self.num_bots+1, i+1)))
                    for results, player_list in zip(self.results[-self.num_bots:], self.player_lists[-self.num_bots:]):
                        arity = len(results)
                        self.diff_results.append(results)
                        self.diff_totals_by_arity[arity] += 1
                        self.diff_wins[player_list[results[0]]] += 1
                        for place, j in enumerate(results):
                            player_name = player_list[j]
                            self.diff_placements[player_name, arity, place] += 1

    def print_win_data(self):
        """
        Print the results.
        """
        print("==========================")
        print("Tournament Results {}/{} games:".format(self.games_played, self.number_of_games))
        for name in self.program_names:
            error_note = ""
            if self.games_with_errors[name]:
                error_games = ", ".join(map(str, self.games_with_errors[name]))
                error_note += "(Errors on games {}) ".format(error_games)

            if self.games_with_warnings[name]:
                warnings_games = self.games_with_warnings[name]
                if len(warnings_games) > 5:
                    warnings_games = ["..."] + warnings_games[-5:]
                warning_str = ", ".join(map(str, warnings_games))
                error_note += "(Warnings on games {}) ".format(warning_str)

            print("{} : {} [{}] wins {}".format(name, self.wins[name], self.diff_wins[name], error_note))

            for arity in (2, 3, 4):
                if self.totals_by_arity[arity]:
                    stats = ["{}. {:3} [{:3}] ".format(i+1, self.placements[name, arity, i],
                                                       self.diff_placements[name, arity, i]) for i in range(arity)]
                    print("   ", arity, "player games: ", *stats)
        if self.games_to_look_at:
            print("Games where results differ:", *self.games_to_look_at)
        print("Total tournament time:", time.perf_counter() - self.start_time, "sec")
