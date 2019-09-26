# -*- coding: utf-8 -*-

import time
import traceback
from pprint import pprint
from emulator import Emulator

t = time.perf_counter()
emu = Emulator(
    'https://www.marathonbet.ru/su/',
    browser='chrome',
    headless=False,
    no_betting=True,
    proxy_type='',
    proxy_host='127.0.0.1',
    proxy_port='39723',
    proxy_login='',
    proxy_password=''
)
emu.login('login', 'password')
user_bk_info = emu.get_user_bk_info()
print(user_bk_info)
try:
    emu.place_bet('Футбол', 'Валенсия', 'Янг Бойз', 1., 15.5)
    print('Ставка сделана!')
except Exception as e:
    print('Не удалось сделать ставку.')
    pprint(e)
    traceback.print_exc()
print('Время: {}'.format(time.perf_counter() - t))

input()
