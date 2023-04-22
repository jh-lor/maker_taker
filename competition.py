from maker_taker_base import Game
from itertools import permutations
import pandas as pd
import numpy as np
import statistics


class Competition:
    def __init__(self, players, rounds=1, time_limit=0):
        self.players = players
        self.rounds = rounds
        self.results = None
        self.summary = None
        self.time_limit = time_limit

    def run_competition(self):
        results = {}
        summary_list = {"maker": [], "taker": [],
                        "maker_pnl": [], "taker_pnl": [], "std": []}
        for maker_player, taker_player in permutations(self.players.keys(), 2):
            maker_class = self.players[maker_player]["maker"]
            taker_class = self.players[taker_player]["taker"]
            game = Game(taker_class, maker_class, timer=self.time_limit)
            results[(taker_player, maker_player)] = [
                game.run_game()
                for rd in range(self.rounds)
            ]
            summary_list["maker"].append(maker_player)
            summary_list["taker"].append(taker_player)
            maker_pnl = [rnd["maker_pnl"]
                         for rnd in results[(taker_player, maker_player)]]
            taker_pnl = [rnd["taker_pnl"]
                         for rnd in results[(taker_player, maker_player)]]
            summary_list["maker_pnl"].append(statistics.mean(maker_pnl))
            summary_list["taker_pnl"].append(statistics.mean(taker_pnl))
            summary_list["std"].append(statistics.stdev(maker_pnl))

        self.results = results
        self.summary = pd.DataFrame(summary_list)

        return self.results, self.summary

    def get_score(self):
        d = {}
        for role in ["maker", "taker"]:
            grouped_scores = self.summary.groupby(role)
            scores = grouped_scores.agg(
                mean=pd.NamedAgg(column=role + "_pnl", aggfunc="mean"),
                std=pd.NamedAgg(column="std",
                                aggfunc=lambda x: np.sqrt(np.sum(x*x))),
                min=pd.NamedAgg(column=role + "_pnl", aggfunc="min")
            )

            scores["nemesis"] = self.summary.loc[
                grouped_scores[role + "_pnl"].idxmin(),
                "maker" if role == "taker" else "taker"
            ].values
            d[role] = scores
        return d
