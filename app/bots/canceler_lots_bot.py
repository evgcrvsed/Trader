from bots.base import BaseBot
from steampy.models import GameOptions, PredefinedOptions
from utils.functions import DataBase
import random
import time


class CancelerBot(BaseBot):
    def process(self):
        listings = self.steam.get_my_market_listings()
        for item in listings['sell_listings']:
            self.logger.info(item)
            self.steam.client.market.cancel_sell_order(item)
        for item in listings['buy_orders']:
            self.logger.info(item)
            self.steam.client.market.cancel_buy_order(item)
