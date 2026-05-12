import os
import json
import time
import random

import requests
from pprint import pprint

from urllib3 import HTTPConnectionPool

from steampy.models import Asset, GameOptions
class ASF:
    def __init__(self):
        self.url = 'http://localhost:1242/Api/Command'
        self.headers = {
        "accept": "application/json",
        "Content-Type": "application/json"}
        self.data = {"data": {"Command": ""}}

    def get_steam_id(self, account_nickname: str = None):
        try:
            response = requests.get(
                f'http://localhost:1242/Api/Bot/{account_nickname}',
                headers=self.headers,
                json=self.data
            )
            result = response.json()
            return int(result['Result'][account_nickname]['SteamID'])
        except Exception as ex:
            print(ex)
            return 0

    def get_steam_inventory(self, steam_id: int = None, game: int = None, retry: bool = True):
        try:
            response = requests.get(
                f"https://steamcommunity.com/inventory/{steam_id}/{game}/2?l=russian",
                headers=self.headers,
                json=self.data
            )
            result = response.json()
            items_name = [item['market_name'] for item in result['descriptions']]
            result = {
                'count': result['total_inventory_count'],
                'items': items_name
            }
            return result
        except Exception as ex:
            if retry:
                print(f'Error when receiving inventory: {steam_id}')
                time.sleep(5)
                return self.get_steam_inventory(steam_id=steam_id, game=game, retry=False)
            return {'count': 0, 'items': []}


    def getbotbanned(self, bot_nickname: str = None):
        try:
            self.data['Command'] = f'getbotbanned {bot_nickname}'
            # print(self.get_steam_id(bot['nickname']))
            req = requests.post(self.url, headers=self.headers, json=self.data).json()
            # pprint(req.json())
            # print(req['Result'])
            # print(req['Result'].find('не подключён!'))
            # input(req['Result'])
            print(req['Result'])
            if req['Result'] == 'No ban records':
                return False
            return True
            # return req['Result']
        except Exception as ex:
            pprint(ex)

    def addfriend(self, main_bot: str, bots):
        try:
            for index, bot in enumerate(bots):
                self.data['Command'] = f"addfriend {main_bot} {self.get_steam_id(bot['nickname'])}"
                # print(self.get_steam_id(bot['nickname']))
                req = requests.post(self.url, headers=self.headers, json=self.data).json()
                # pprint(req.json())
                print(req['Result'])
                print(f'{index+1}/{len(bots)}')
                time.sleep(random.randint(5, 8))
        except Exception as ex:
            pprint(ex)

    def is_online(self, bot_nickname: str) -> bool:
        """Возвращает False если бот не владеет этой игрой"""
        try:
            self.data['Command'] = f'owns {bot_nickname} {123}'
            req = requests.post(self.url, headers=self.headers, json=self.data).json()
            # print(req)
            if req['Result'] is None:
                return False
            else:
                return True

        except Exception as ex:
            print(ex)


    def owns(self, bot_nickname: str, game) -> bool:
        """Возвращает False если бот не владеет этой игрой"""
        try:
            self.data['Command'] = f'owns {bot_nickname} {game}'
            req = requests.post(self.url, headers=self.headers, json=self.data).json()
            # pprint(req)
            if 'Ещё не имеет:' in req['Result']:
                return False
            else:
                return True

        except Exception as ex:
            pass

    def get_balance_type(self, bot_nickname: str) -> str:
        self.data['Command'] = f'balance {bot_nickname}'
        req = requests.post(self.url, headers=self.headers, json=self.data).json()
        return req['Result'].split()[-1]

    def get_balance(self, bot_nickname: str) -> str:
        self.data['Command'] = f'balance {bot_nickname}'
        req = requests.post(self.url, headers=self.headers, json=self.data).json()
        # print(req['Result'])
        return req['Result'].split()[3].replace(',', '.')

    def get_cart_price(self, bot_nickname: str) -> str:
        self.data['Command'] = f'cart {bot_nickname}'
        req = requests.post(self.url, headers=self.headers, json=self.data).json()
        return req['Result'].split()[len(req['Result'].split()) - 2]

    def checkmarketlimit(self, bot_nickname: str) -> bool:
        self.data['Command'] = f'CHECKMARKETLIMIT  {bot_nickname}'
        req = requests.post(self.url, headers=self.headers, json=self.data).json()
        # pprint(req)
        if 'не имеет' in req['Result']:
            return False
        else:
            return True



    def addcartgift_pro(self, main_bot, game_ids, bots):
        games_to_gift = game_ids.split(' ')

        main_acc_balance = self.get_balance(bot_nickname=main_bot)

        data = {}
        for game in games_to_gift:
            data[game] = 0

        for index, acc in enumerate(bots):
            # print(f'{index + 1}/{len(bots)}')

            for item in games_to_gift:
                if self.owns(acc['nickname'], f'sub/{item}'):
                    data[item] += 1

        pprint(data)
        while True:
            min_game_count = min(list(data.values()))
            min_game_id = [key for key, value in data.items() if value == min_game_count][0]



            time.sleep(1000)




        input()



    def addcartgift(self, main_bot: str, bots, game):
        self.data['Command'] = f'cartreset {main_bot}'
        requests.post(self.url, headers=self.headers, json=self.data).json()
        time.sleep(3)
        self.data['Command'] = f'addcart {main_bot} {game}'
        requests.post(self.url, headers=self.headers, json=self.data).json()
        input('У основного бота проверь корзину, правильная ли игра и нажми ентер: ')

        games_sent_count = 0
        cart_len = 0
        self.data['Command'] = f'cartreset {main_bot}'
        requests.post(self.url, headers=self.headers, json=self.data).json()
        main_bot_balance_type = self.get_balance_type(main_bot)
        # time.sleep(random.randint(10, 15))
        for index, bot in enumerate(bots):
            print(f'{index + 1}/{len(bots)}')
            print(f'Подарков в корзине: {cart_len}')
            print(f'Отправлено подарков: {games_sent_count}/9')

            print(f'\nБот {bot["nickname"]}')

            is_bot_owns = self.owns(bot['nickname'], game)
            if is_bot_owns:
                print(f'Уже имеет эту игру!')
                continue
            print('Не имеет эту игру!')

            is_bot_market_limit = self.checkmarketlimit(bot['nickname'])
            if is_bot_market_limit:
                print(f'Имеет закрытую торговую площадку!')
                continue
            print(f'Имеет открытую торговую площадку!')

            bot_balance_type = self.get_balance_type(bot['nickname'])
            if bot_balance_type != main_bot_balance_type:
                print(f'Валюта бота {bot_balance_type}, основы: {main_bot_balance_type}, дарить нельзя!')
                continue
            print(f'Валюта бота {bot_balance_type}, основы: {main_bot_balance_type}, дарить можно!')

            self.data['Command'] = f"addcartgift {main_bot} {game} {self.get_steam_id(bot['nickname'])}"
            requests.post(self.url, headers=self.headers, json=self.data).json()
            time.sleep(random.randint(5, 10))
            cart_len += 1
            # addcartgift eevgeniy4 sub/68915 botnick
            if cart_len >= 15:
                self.data['Command'] = f'purchase {main_bot}'
                req = requests.post(self.url, headers=self.headers, json=self.data).json()
                pprint(req['Result'])
                time.sleep(5)
                # input('Оплачивай корзину!')
                self.data['Command'] = f'cartreset {main_bot}'
                requests.post(self.url, headers=self.headers, json=self.data).json()
                cart_len = 0
                games_sent_count += 1



            if games_sent_count == 9:
                print('Отправлено 9 подарков, нужно подождать!')
                return
            # self.data['Command'] = f'purchase {main_bot}'
            # req = requests.post(self.url, headers=self.headers, json=self.data).json()
            # pprint(req['Result'])

    def auto_confirm(self, bot_name: str):
        self.data['Command'] = f'2faok {bot_name}'
        try:
            requests.post(self.url, headers=self.headers, json=self.data)
        except Exception as ex:
            pass

    def make_review(self, bot_name: str, game_id: int, review: str):
        self.data['Command'] = f'PUBLISHRECOMMENT {bot_name} +{game_id} {review}'
        try:
            response = requests.post(self.url, headers=self.headers, json=self.data)
        except Exception as ex:
            print(f'Произошла ошибка:')
            print(ex)
            time.sleep(600)


    def send_all_inventory_farm(self, inpt: str = None, gamee: str = None):
        for i in range(1, 3):
            # print(i)
            self.data['Command'] = f'transfer^ ASF {gamee} {i} {inpt}'
            # print(self.data['Command'])

            try:
                requests.post(self.url, headers=self.headers, json=self.data)
            except Exception as ex:
                print(f'Произошла ошибка:')
                print(ex)

    def stackinventory(self, login: str, game: GameOptions):
        # print(i)
        if game.app_id == '753':
            print('Стак отменён: карточки не стакаются')
            return
        self.data['Command'] = f'STACKINVENTORY {login} {game.app_id} {game.context_id}'
        # print(self.data['Command'])

        try:
            requests.post(self.url, headers=self.headers, json=self.data)
        except HTTPConnectionPool:
            print('ASF не запущен!')
        except Exception as ex:
            print(f'Произошла ошибка:')
            print(ex)

    def add_game(self, game_code: int) -> None:
        """Добавляем лицензию игры всем ботам"""
        self.data['Command'] = f'addlicense ASF app/{game_code}'
        try:
            requests.post(self.url, headers=self.headers, json=self.data)
        except Exception as ex:
            pass
