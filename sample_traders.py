from maker_taker_base import Taker, Maker, Side, Market, test
import random
from typing import Type
from time import sleep


class BullishTaker(Taker):
    def do_trade(self, market: Type[Market], round: int) -> Type[Side]:
        return Side.buy


class BearishTaker(Taker):
    def do_trade(self, market: Type[Market], round: int) -> Type[Side]:
        return Side.sell


class RandomTaker(Taker):
    def do_trade(self, market: Type[Market], round: int) -> Type[Side]:
        return random.choice([Side.buy, Side.sell])


class GreedyTaker(Taker):
    def do_trade(self, market: Type[Market], round: int) -> Type[Side]:
        return market.better_side(self.true_value)


class CenterMaker(Maker):
    def get_market(self, round: int) -> Market():
        return Market(45, 1, 55, 1)

    def update_trade(self, side: Type[Side]) -> None:
        return


class RandomMaker(Maker):
    def get_market(self, round: int) -> Market():
        fair = random.randint(5, 95)
        return Market(fair-5, 1, fair+5, 1)

    def update_trade(self, side: Type[Side]) -> None:
        return


class FaderMaker(Maker):
    side_map = {Side.buy: 1, Side.sell: -1, Side.notrade: 0}

    def __init__(self) -> None:
        self.fair = 50

    def get_market(self, round: int) -> Market():
        return Market(self.fair - 5, 1, self.fair + 5, 1)

    def update_trade(self, side: Type[Side]) -> None:
        self.fair += self.side_map[side] * 10


def main():
    # test(GreedyTaker, CenterMaker)
    test(GreedyTaker, FaderMaker)


if __name__ == "__main__":
    main()
