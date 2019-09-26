# -*- coding: utf-8 -*-

import traceback
import os
import re
from datetime import datetime
from time import sleep
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import *
from user_bk_info import UserBkInfo
from bet import Bet

class Emulator:
    """Эмулятор ставок"""

    def __init__(self, url, headless=True, browser='chrome', no_betting=False, proxy_type='', proxy_host='', proxy_port='', proxy_login='', proxy_password=''):
        """Конструктор
        :param url: Адрес БК
        :param headless: Запускать в режиме "без GUI"
        :param no_betting: Не делать ставку
        :param proxy_type: Тип прокси
        :param proxy_host: Хост прокси
        :param proxy_port: Порт прокси
        :param proxy_login: Логин прокси
        :param proxy_password: Пароль прокси
        """
        self.url = url
        self.no_betting = no_betting
        # Сколько ждать до появления элементов на странице
        self.timeout = 20
        # Дополнительные опции для браузера
        if browser == 'firefox':
            capabilities = DesiredCapabilities.FIREFOX
            options = FirefoxOptions()
        elif browser == 'chrome':
            capabilities = DesiredCapabilities.CHROME
            capabilities['pageLoadStrategy'] = 'none'
            options = ChromeOptions()
            options.add_argument('--disable-infobars')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--window-size=1600,920')
            options.add_argument('--log-level=3')
            if proxy_type:
                print('--proxy-server={}'.format(self.make_proxy_link(proxy_type, proxy_host, proxy_port, proxy_login, proxy_password)))
                options.add_argument('--proxy-server={}'.format(self.make_proxy_link(proxy_type, proxy_host, proxy_port, proxy_login, proxy_password)))
        else:
            raise UnsupportedBrowser()
        # Можно запустить без GUI (для серверов)
        if headless:
            options.add_argument('--headless')
        # Создаём наш браузер
        if browser == 'firefox':
            self.browser = webdriver.Firefox(firefox_options=options)
        elif browser == 'chrome':
            self.browser = webdriver.Chrome(chrome_options=options, desired_capabilities=capabilities)
        else:
            raise UnsupportedBrowser()

    def __del__(self):
        # Закрываем браузер
        try:
            self.browser.quit()
        except:
            pass

    def make_proxy_link(self, type, host, port, login='', password=''):
        """Создает строку подключения прокси"""
        login_string = '' # login_string = '{}:{}@'.format(login, password)
        if type == 'http':
            prefix_string = 'http://'
        elif type == 'ssl':
            prefix_string = 'https://'
        else:
            prefix_string = ''
        return '{}{}{}:{}'.format(prefix_string, login_string, host, port)

    def __wait_for_element_by_id(self, id, should_be_visible=False):
        """Ждет появления элемента по ID
        :param id: DOM id
        :param should_be_visible: Если true, то элемент обязан быть видимым на странице
        """
        method = EC.visibility_of_element_located if should_be_visible else EC.presence_of_element_located
        WebDriverWait(self.browser, self.timeout).until(
            method((By.ID, id))
        )

    def __wait_for_element_by_class_name(self, class_name, should_be_visible=False):
        """Ждет появления элемента по css-классу
        :param class_name: DOM class
        :param should_be_visible: Если true, то элемент обязан быть видимым на странице
        """
        method = EC.visibility_of_element_located if should_be_visible else EC.presence_of_element_located
        WebDriverWait(self.browser, self.timeout).until(
            method((By.CLASS_NAME, class_name))
        )

    def __wait_for_element_by_text(self, text, should_be_visible=False):
        """Ждет появления элемента содержащего указанный текст
        :param text: Текст элемента
        :param should_be_visible: Если true, то элемент обязан быть видимым на странице
        """
        method = EC.visibility_of_element_located if should_be_visible else EC.presence_of_element_located
        WebDriverWait(self.browser, self.timeout).until(
            method((By.XPATH, '//*[contains(text(), "{}")]'.format(text)))
        )

    def __wait_for_element_by_xpath(self, xpath, should_be_visible=False):
        """Ждет появления элемента по xpath
        :param xpath: Xpath
        :param should_be_visible: Если true, то элемент обязан быть видимым на странице
        """
        method = EC.visibility_of_element_located if should_be_visible else EC.presence_of_element_located
        WebDriverWait(self.browser, self.timeout).until(
            method((By.XPATH, xpath))
        )

    def __wait_for_element_to_be_clickable_by_id(self, id):
        """Ждет кликабельности элемента по ID
        :param id: DOM id
        """
        WebDriverWait(self.browser, self.timeout).until(
            EC.element_to_be_clickable((By.ID, id))
        )

    def __wait_for_element_to_be_clickable_by_xpath(self, xpath):
        """Ждет кликабельности элемента по Xpath
        :param xpath: Xpath
        """
        WebDriverWait(self.browser, self.timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

    def __click_element(self, el, id='', xpath=''):
        """Кликает по элементу
        :pram el: Элемент
        :param id: Если указан DOM id, ждём повления элемента по нему
        :param xpath: Если указан xpath, ждём повления элемента по нему
        """
        if id:
            self.__wait_for_element_to_be_clickable_by_id(id)
        if xpath:
            self.__wait_for_element_to_be_clickable_by_xpath(xpath)
        actions = webdriver.ActionChains(self.browser)
        actions.move_to_element_with_offset(el, 5, 5)
        actions.click(el)
        actions.perform()

    def __move_to_element(self, el):
        """Переходит к элементу"""
        self.browser.execute_script('arguments[0].scrollIntoView(true);', el)
        sleep(0.5)

    def __click_with_js(self, el, id='', xpath=''):
        """Эмулирует клик по элементу с помощью JavaScript
        :pram el: Элемент
        :param id: Если указан DOM id, ждём повления элемента по нему
        :param xpath: Если указан xpath, ждём повления элемента по нему
        """
        if id:
            self.__wait_for_element_to_be_clickable_by_id(id)
        if xpath:
            self.__wait_for_element_to_be_clickable_by_xpath(xpath)
        self.browser.execute_script('arguments[0].click();', el)

    def __set_value_by_id(self, id, value):
        """Устанавливает value элемента"""
        self.browser.execute_script("document.getElementById('{}').setAttribute('value', '{}')".format(id, value))

    def __try_clicking(self, el):
        """Пытается кликать элемент несколько раз"""
        for _ in range(8):
            try:
                self.__click_with_js(el)
                return
            except:
                pass
            sleep(0.5)
        self.__click_element(el)

    def make_url(self, path):
        """Формирует URL для сайта"""
        return '{}{}'.format(self.url, path)

    def make_screenshot(self, path, name = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f"))):
        """Создаёт скриншот по указанному пути"""
        try:
            path = os.path.join(path, name + '.png')
            self.browser.save_screenshot(path)
        except:
            pass

    def login(self, login, password):
        """Вход на сайт
        :param login: Логин
        :param password: Пароль
        """
        self.browser.get(self.make_url('live/popular'))
        # Дожидаемся показа нужных элементов и действуем не ожидая остальных
        WebDriverWait(self.browser, self.timeout).until(
            EC.presence_of_element_located((By.ID, 'container_POPULAR_EVENTS'))
        )
        WebDriverWait(self.browser, self.timeout).until(
            EC.presence_of_element_located((By.ID, 'auth_login'))
        )
        for _ in range(3):
            try:
                # Вводим логин
                login_input = self.browser.find_element_by_id('auth_login')
                login_input.send_keys(login)
                # Вводим пароль
                self.__set_value_by_id('auth_login_password', password)
                # Жмём Войти
                login_button = self.browser.find_element_by_css_selector('.login')
                login_button.click()
                # Ждём завершения входа
                self.__wait_for_element_by_id('header_balance')
                return
            except:
                login_input = self.browser.find_element_by_id('auth_login')
                login_input.clear()
            sleep(1)
        # Вводим логин
        login_input = self.browser.find_element_by_id('auth_login')
        login_input.send_keys(login)
        # Вводим пароль
        self.__set_value_by_id('auth_login_password', password)
        # Жмём Войти
        login_button = self.browser.find_element_by_css_selector('.login')
        login_button.click()
        # Ждём завершения входа
        self.__wait_for_element_by_id('header_balance')

    def go_to_live(self):
        """Переход на страницу LIVE"""
        self.browser.get(self.make_url('live/popular'))

    def open_live_menu(self, category):
        """Открывает LIVE-меню для указанного спорта
        :param category: Название спорта
        """
        xpath = '//*[@id="leftMenuPanel"]//*[contains(text(), "{}")]/ancestor::div[1]/ancestor::div[1]'.format(category)
        self.__wait_for_element_by_xpath(xpath)
        menu_item = self.browser.find_element_by_xpath(xpath)
        dropdown_button = menu_item.find_element_by_class_name('dropdown')
        dropdown_button.click()

    def open_live_game(self, team1, team2):
        """Открывает страницу матча
        :param team1: Команда 1
        :param team2: Команда 2
        """
        try:
            menu_item = self.browser.find_element_by_xpath('//*[@id="leftMenuPanel"]//a[contains(text(), "{} - {}")]'.format(team1, team2))
        except NoSuchElementException:
            try:
                menu_item = self.browser.find_element_by_xpath('//*[@id="leftMenuPanel"]//a[contains(text(), "{} - {}")]'.format(team2, team1))
            except NoSuchElementException:
                raise TeamsNotFound('{} - {}'.format(team1, team2))
        self.__move_to_element(menu_item)
        self.__click_with_js(menu_item)
        self.__wait_for_element_by_text('Все выборы')

    def open_totals(self):
        """Переходит на вкладку Тоталы"""
        try:
            totals_button = self.browser.find_element_by_xpath('//*[contains(text(), "Тоталы")]')
        except:
            raise TotalNotFound()
        self.__click_with_js(totals_button, False, '//*[contains(text(), "Тоталы")]')
        self.__wait_for_element_by_text('Тотал голов')
        sleep(0.5)

    def find_betting_button(self, container, coefficient):
        """Находит кнопочку для ставок
        :param container: Элемент, в котором искать кнопки
        :param coefficient: Коэффициент
        """
        # Находим кнопочки для ставок
        price_items = container.find_elements_by_css_selector('[data-selection-price]')
        # Оставляем только кнопочки "Меньше"
        price_items_under = [x for x in price_items if '.Under_' in x.get_attribute('data-selection-key')]
        # Оставляем только кнопочки с коээфициентом > указанного
        price_items_coefficient = [x for x in price_items_under if float(x.get_attribute('data-selection-price')) > coefficient]
        if len(price_items_coefficient) == 0:
            raise NothingToBet()
        return price_items_coefficient[-1]

    def click_betting_button(self, loser, coefficient):
        """Нажимает кнопочку добавления ставки
        Если не получается, пробует ещё раз. Такое необходимо, т.к. кнопки периодически обновляются.
        :param loser: Команда-лузер
        :param coefficient: Коэффициент
        """
        for _ in range(30):
            try:
                # Находим вкладку, где лежат ставки
                container = self.browser.find_element_by_xpath('//*[normalize-space(text())="Тотал голов ({})"]/ancestor::div[1]'.format(loser))
                self.__move_to_element(container)
                button = self.find_betting_button(container, coefficient)
                self.__move_to_element(button)
                self.__click_with_js(button)
                return
            except NothingToBet:
                raise NothingToBet
            except:
                pass
            sleep(1.5)
        container = self.browser.find_element_by_xpath('//*[normalize-space(text())="Тотал голов ({})"]/ancestor::div[1]'.format(loser))
        button = self.find_betting_button(container, coefficient)
        self.__move_to_element(button)
        self.__click_with_js(button)

    def bet_loser_totals_by_coefficient(self, loser, coefficient, sum):
        """Делает ставку на лузера по коэффициенту
        :param loser: Команда-лузер
        :param coefficient: Коэффициент
        :param sum: Сумма ставки
        """
        # Нажимает кнопку ставки
        self.click_betting_button(loser, coefficient)
        # Вбиваем сумму ставки
        self.__wait_for_element_by_class_name('stake-input')
        stake_input = self.browser.find_element_by_class_name('stake-input')
        stake_input.send_keys(str(sum))
        # Нажимаем кнопку создания ставки
        bet_button = self.browser.find_element_by_id('betslip_placebet_btn_id')
        if not self.no_betting:
            bet_button.click()
            self.__wait_for_element_by_id('betresult', True)

    def quit(self):
        """Выходит с сайта"""
        sleep(0.5)
        button = self.browser.find_element_by_id('logoutLink')
        self.__move_to_element(button)
        self.__click_with_js(button)

    def place_bet(self, category, winner, loser, coefficient, sum):
        """Автоматически делает ставку с указанными параметрами
        :param category: Вид спорта
        :param winner: Команда-победитель
        :param loser: Команда-лузер
        :param coefficient: Коэффициент, выше которого ставка делается
        :param sum: Сумма ставки
        """
        self.open_live_menu(category)
        self.open_live_game(winner, loser)
        self.open_totals()
        self.bet_loser_totals_by_coefficient(loser, coefficient, sum)
        self.quit()
    
    def get_user_bk_info(self):
        """Получает данные аккаунта пользователя"""
        self.browser.get(self.make_url('myaccount/myaccount.htm'))
        WebDriverWait(self.browser, self.timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'history-result'))
        )
        # Вытягиваем основной баланс
        total_summ_element = self.browser.find_element_by_css_selector('[data-punter-balance-value]')
        total_summ = float(total_summ_element.get_attribute('data-punter-balance-value'))
        # Вытягиваем нерассчитанные ставки
        bets_summ_element = self.browser.find_element_by_xpath('//*[contains(text(), "Нерассчитанные")]/ancestor::tr/*[contains(@class, "value")]')
        bets_summ = float(re.sub('[^.0-9]', '', bets_summ_element.text))
        # Вытягиваем историю пари
        bets = []
        history_results = self.browser.find_elements_by_class_name('history-result-main')
        for history_result in history_results:
            # Выплата
            result = history_result.find_element_by_class_name('result').text.strip().replace('₽ ', '')
            try:
                result = float(result)
            except:
                result = None
            # Статус ставки
            open_bet_element = history_result.find_element_by_class_name('open-bet')
            open_bet = -1
            try:
                open_bet_element.find_element_by_xpath('*[contains(@src, "win-icon")]')
                open_bet = 1
            except:
                try:
                    open_bet_element.find_element_by_xpath('*[contains(@src, "lose-icon")]')
                    open_bet = 0
                except:
                    pass
            # Добавляем запись истории
            bets.append(
                Bet(
                    history_result.find_element_by_class_name('bet-number').text.strip(),
                    history_result.find_element_by_class_name('date').text.strip(),
                    history_result.find_element_by_class_name('bet-title').find_elements_by_tag_name('span')[1].text.strip(),
                    float(re.sub('[^.0-9]', '', history_result.find_element_by_class_name('total-stake').text)),
                    result,
                    float(history_result.find_element_by_class_name('coefficient').text.strip()),
                    open_bet
                )
            )
        return UserBkInfo(total_summ, bets_summ, bets)

class TeamsNotFound(Exception):
    """Исключение при невозможности найти играющие команды"""
    pass

class TotalNotFound(Exception):
    """Исключение при невозможности найти тоталы"""
    pass

class NothingToBet(Exception):
    """Исключение при невозможности сделать ставку с указанными условиями"""
    pass

class UnsupportedBrowser(Exception):
    """Исключение при неподдерживаемом браузере"""
    pass
