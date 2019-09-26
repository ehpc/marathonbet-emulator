# -*- coding: utf-8 -*-

from pprint import pprint

class Bet:
    """Ставка в БК"""

    def __init__(self, id, dtime = None, game_name = None, bet_summ = 0, win_summ = 0, bet_koef = 0, status = 0):
        """
        :param id: Из столбца "#"
        :param dtime: Из столбца "Дата"
        :param game_name: Из столбца "Ставка в пари" нижняя строчка обычный шрифт
        :param bet_summ: Из столбца "Сумма"
        :param win_summ: Из столбца "Выплата"
        :param bet_koef: Из столбца "Коэфф."
        :param status: Статус ставки: -1 - не расчитанна, 0 - проигрыш, 1 - выигрыш
        """
        self.id = id
        self.dtime = dtime
        self.game_name = game_name
        self.bet_summ = bet_summ
        self.win_summ = win_summ
        self.bet_koef = bet_koef
        self.status = status

    def __str__(self):
        return str(vars(self))
