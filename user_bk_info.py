# -*- coding: utf-8 -*-

from pprint import pprint

class UserBkInfo:
    """Класс инфа о пользователе в БК"""

    def __init__(self, total_summ, bets_summ, bets):
        """
        :param total_summ: Текущий основной баланс
        :param bets_summ: Сумма нерасчитаных ставок в пари
        :param bets: Список ставок
        """
        self.total_summ = total_summ
        self.bets_summ = bets_summ
        self.bets = bets

    def __str__(self):
        return "total_summ: {}\nbets_summ: {}\nbets: {}".format(self.total_summ, self.bets_summ, [str(x) for x in self.bets])
