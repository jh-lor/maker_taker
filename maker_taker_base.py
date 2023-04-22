# IMPORTS
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Type
from attr import dataclass
from timeout_utils import run_function_with_time_limit

# Maker Trader Game
# 0 to 100, Maker makes two sided market with unlimited size, taker chooses which side to take.
# Three rounds. Taker is Obliged to trade. Taker knows true value. Taker has to trade on 10 or narrower market
# No guaranteed trade if large than 10

MAX_SIZE = 1000
ROUNDS = 3


class Side(Enum):
    buy = auto()
    sell = auto()
    notrade = auto()

    def opposite(self):
        if self == Side.buy:
            return Side.sell
        elif self == Side.sell:
            return Side.buy
        else:
            return Side.notrade


@dataclass
class Market:
    bid: int = 0
    bid_size: int = 1
    ask: int = 100
    ask_size: int = 1

    def width(self) -> int:
        return self.ask - self.bid

    def better_side(self, true_value) -> Type[Side]:
        return Side.buy if (self.bid-true_value)*self.bid_size < (true_value - self.ask) * self.ask_size else Side.sell


@dataclass
class TradeLog():
    true_value: int
    market: Type[Market]
    side: Side
    taker_contracts: int
    taker_cash: int
    maker_contracts: int
    maker_cash: int


class Game():
    def __init__(self, taker, maker, timer=.1) -> None:
        if not (issubclass(taker, Taker) and issubclass(maker, Maker)):
            raise Exception("Need to provide a Taker and a Maker")
        self.taker_class = taker
        self.maker_class = maker
        self.timer = timer

    def run_game(self, seed=0, true_value=None) -> dict:
        if not true_value:
            if seed:
                random.seed(seed)
            true_value = random.randint(0, 100)
        taker = self.taker_class(true_value)
        maker = self.maker_class()
        pos = {"taker": {"contracts": 0, "cash": 0},
               "maker": {"contracts": 0, "cash": 0}}
        log = []
        for round in range(ROUNDS):
            market = Market()
            if self.timer > 0:
                t_market = run_function_with_time_limit(
                    maker.get_market, round, timer=self.timer)
                if t_market is not None:
                    market = t_market
            else:
                market = maker.get_market(round)

            market.bid_size = max(min(market.bid_size, MAX_SIZE), 1)
            market.ask_size = max(min(market.ask_size, MAX_SIZE), 1)

            if (market.width() > 10):
                pos["maker"]["cash"] += - 100
                market = Market(45, 1, 55, 1)

            side = Side.notrade
            if self.timer > 0:
                t_side = run_function_with_time_limit(
                    taker.do_trade, market, round, timer=self.timer)
                if t_side is not None:
                    side = t_side
            else:
                taker.do_trade(market, round)

            if side == Side.notrade and market.width() <= 10:
                side = Side.buy
                pos["taker"]["cash"] += -100
            if side == Side.buy:
                cash = market.ask*market.ask_size
                pos["taker"]["contracts"] += market.ask_size
                pos["taker"]["cash"] += -cash
                pos["maker"]["contracts"] += - market.ask_size
                pos["maker"]["cash"] += cash
            elif side == Side.sell:
                cash = market.bid*market.bid_size
                pos["taker"]["contracts"] += -market.bid_size
                pos["taker"]["cash"] += cash
                pos["maker"]["contracts"] += market.bid_size
                pos["maker"]["cash"] += -cash
            elif side != Side.notrade:
                raise Exception("Invalid Side")

            if self.timer > 0:
                run_function_with_time_limit(
                    maker.update_trade, side, timer=self.timer)
            else:
                maker.update_trade(side)

            log.append(TradeLog(true_value, market, side, pos["taker"]["contracts"],
                       pos["taker"]["cash"], pos["maker"]["contracts"], pos["maker"]["cash"]))

        return {"taker_pnl": pos["taker"]["cash"] + true_value*pos["taker"]["contracts"],
                "maker_pnl": pos["maker"]["cash"] + true_value*pos["maker"]["contracts"],
                "log": log}


class Maker():
    def __init__(self) -> None:
        pass

    def get_market(self, round: int) -> Market():
        return Market()

    def update_trade(self, side: Type[Side]) -> None:
        return


class Taker():
    def __init__(self, true_value=50) -> None:
        self.true_value = true_value

    def do_trade(self, market: Type[Market], round: int) -> Type[Side]:
        return Side.notrade


def test(taker, maker) -> None:
    game = Game(taker, maker)
    results = game.runGame()
    print("taker_pnl: ", results['taker_pnl'])
    print("maker_pnl: ", results['maker_pnl'])
    for log in results["log"]:
        print(log)


def main() -> int:
    test(Taker, Maker)
    return 0


if __name__ == "__main__":
    main()
