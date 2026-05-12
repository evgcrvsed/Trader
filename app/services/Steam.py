from steampy.client import SteamClient
from steampy.models import GameOptions

from utils.functions import DataBase

from core import config


import time

import os, pickle

class Steam:
    def __init__(self, username, password, steamid, shared_secret, identity_secret, api_key=None):
        self.client: SteamClient = SteamClient(api_key=api_key if api_key else 'shared_secret')
        self.username = username
        self.password = password
        self.steamid = steamid
        self.shared_secret = shared_secret
        self.identity_secret = identity_secret

    def auth(self, new=True):
        file_path = f'data/{self.username}.pkl'

        if new and os.path.exists(file_path):
            os.remove(file_path)

        if not os.path.exists(file_path):
            print('Авторизация...')
            # return
            steam_json = {
                'username': self.username,
                'nickname': self.username,
                'password': self.password,
                'steamid': self.steamid,
                'shared_secret': self.shared_secret,
                'identity_secret': self.identity_secret,
            }
            db = DataBase(f'{self.username}')
            db.set_data(steam_json)
            self.client.login(self.username, self.password, f'data/{self.username}.json')
            os.remove(f'data/{self.username}.json')

            with open(file_path, 'wb') as f:
                pickle.dump(self.client, f)
        else:
            with open(file_path, 'rb') as f:
                self.client = pickle.load(f)
            with open(file_path, 'wb') as f:
                pickle.dump(self.client, f)

        try:

            return self.client.get_my_g_rgWalletInfo()
        except Exception:
            print('Не получилось авторизоваться, надо перезайти...')

            os.remove(file_path)
            exit(0)

    def get_inventory(self, game: GameOptions) -> dict:
        return self.client.get_my_inventory(game=game)

    def get_item_price(self, appid, contextid, item_hash_name: str) -> int:
        return self.client.market.multibuy(appid, contextid, item_hash_name)

    def parse_game(self, appid, count):
        return self.client.market.get_game(appid, count)

    def get_item_id(self, url):
        return self.client.market.get_item_id(url)

    def get_item_itemordershistogram(self, item_nameid):
        return self.client.market.itemordershistogram(item_nameid)

    def get_my_market_listings(self):
        return self.client.market.get_my_market_listings()

    def get_my_g_rgWalletInfo(self):
        return self.client.get_my_g_rgWalletInfo()

    def get_item_price_from_total(self, nTotal: int) -> int:
        # Захардкоженные данные кошелька (как в твоём JS)
        g_rgWalletInfo = self.g_rgWalletInfo

        # === Вспомогательные функции внутри (чтобы всё было в одной функции) ===

        def ToValidMarketPrice(nPrice: int) -> int:
            nFloor = int(g_rgWalletInfo.get('wallet_market_minimum', 1))
            nIncrement = int(g_rgWalletInfo.get('wallet_currency_increment', 1))

            if nPrice <= nFloor:
                return nFloor
            if nPrice <= nIncrement:
                return nIncrement
            if nIncrement > 1:
                dAmount = nPrice / nIncrement
                dSign = -1 if dAmount < 0 else 1
                dAmount = dSign * int(abs(dAmount) + 0.5) * nIncrement
                return int(dAmount)
            return nPrice

        def CalculateFee(base_amt: int, pct: float) -> int:
            if pct > 0:
                return ToValidMarketPrice(int(base_amt * pct))
            return 0

        def GetTotalWithFees(base_amt: int, ppct: float, spct: float) -> int:
            nBase = ToValidMarketPrice(base_amt)
            nPubFee = CalculateFee(base_amt, ppct)
            nSteamFee = CalculateFee(base_amt, spct)
            return nBase + nPubFee + nSteamFee

        # === Основная логика GetItemPriceFromTotal ===

        ppct = float(g_rgWalletInfo.get('wallet_publisher_fee_percent_default', 0.1))
        spct = float(g_rgWalletInfo.get('wallet_fee_percent', 0.05))
        nIncrement = int(g_rgWalletInfo.get('wallet_currency_increment', 1))
        nFloor = int(g_rgWalletInfo.get('wallet_market_minimum', 1))

        # Начальное приближение
        nInitialGuess = int(nTotal / (1.0 + ppct + spct))
        nMaxBase = nTotal - 2 * nFloor

        # Приводим к валидной цене
        nBase = ToValidMarketPrice(min(nInitialGuess, nMaxBase))

        # Пытаемся подобрать точное значение (максимум 3 итерации, как в оригинале)
        for _ in range(3):
            nCalculated = GetTotalWithFees(nBase, ppct, spct)

            if nCalculated == nTotal:
                return nBase

            if nCalculated < nTotal:
                nBase += nIncrement
            else:
                nBase -= nIncrement
                break

        return max(nFloor, nBase)

