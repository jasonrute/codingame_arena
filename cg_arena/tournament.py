import random
import time

from match import Match

####################
# Tournament class #
####################

class Tournament():
    def __init__(self, number_of_games, program_names, game_arity, time_limits, verbose, show_map):
        self.number_of_games = number_of_games
        self.program_names = program_names
        self.num_bots = len(self.program_names)
        self.game_arity = game_arity
        self.time_limits = time_limits
        self.verbose = verbose
        self.show_map = show_map

        self.results = []
        self.player_lists = []
        self.wins = {p:0 for p in program_names}
        self.placements = {(p,a,i):0 for p in program_names for a in (2,3,4) for i in range(a)}
        self.totals_by_arity = {a:0 for a in (2,3,4)}
        self.diff_results = []
        self.diff_totals_by_arity = {a:0 for a in (2,3,4)}
        self.diff_wins = {p:0 for p in program_names}
        self.diff_placements = {(p,a,i):0 for p in program_names for a in (2,3,4) for i in range(a)}
        self.games_with_errors = {p:[] for p in program_names}
        self.games_with_warnings = {p:[] for p in program_names}
        self.games_played = 0
        self.games_to_look_at = []

        self.start_time = time.perf_counter()

    def generate_random_configurations(self):
        if self.game_arity:
            game_arity = self.game_arity
        else:
            game_arity = 2 # this is just a two player game

        num_bots = self.num_bots
        player_order = None
        # get random configuration so that not all one playuer
        while player_order == None or all(i==player_order[0] for i in player_order):
            player_order = [random.randrange(num_bots) for _ in range(game_arity)]

        # Find random starting configuration and encode using CG format
        config_str = ""

        # This is specific to Wonder Women

        map_index = random.randrange(3)
        seed = random.randrange(2**32)
        config_str = "mapIndex={};seed={}".format(map_index, seed)
        random_configs = [(player_order, config_str)]


        # rotate players to give some semplance of symmetry (esp in 2 bot case)
        random_configs = []
        for i in range(num_bots):
            player_list = [self.program_names[(j+i) % num_bots] for j in player_order]
            random_configs.append((player_list, config_str))


        return random_configs

    def play_game(self, id_number, player_list, config_str):
        try:
            # Initiallization
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
            for p in match.player_processes:
                if p: p.kill()

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
                        for place, i in enumerate(results):
                            player_name = player_list[i]
                            self.diff_placements[player_name, arity, place] += 1


    def print_win_data(self):
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
                    stats = ["{}. {:3} [{:3}] ".format(i+1, self.placements[name, arity, i], self.diff_placements[name, arity, i]) for i in range(arity)]
                    print("   ", arity, "player games: ", *stats)
        if self.games_to_look_at:
            print("Games where results differ:", *self.games_to_look_at)
        print("Total tournament time:", time.perf_counter() - self.start_time, "sec")