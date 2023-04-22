from maker_taker_base import Taker, Maker, Side, Market
from typing import Type


class Taker(Taker):
    def do_trade(self, market: Type[Market], round: int) -> Type[Side]:
        return Side.buy


class Maker(Maker):
    def get_market(self, round: int) -> Market():
        return Market(45, 1, 55, 1)

    def update_trade(self, side: Type[Side]) -> None:
        return
