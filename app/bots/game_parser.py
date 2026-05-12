# bots/market_bot.py

from bots.base import BaseBot
from utils.functions import *


class ParserBot(BaseBot):
    def __init__(self, steam, asf, game_for_parsing, count_of_pages):
        super().__init__(steam=steam, asf=asf)
        self.game_for_parsing = game_for_parsing
        self.count_of_pages = count_of_pages

    def process(self):

        # step 1 - parsing links
        if os.path.exists(f'data/{self.game_for_parsing}.json'):
            self.logger.info(f'Игра уже собрана: {self.game_for_parsing}')
            return

        data = self.steam.parse_game(self.game_for_parsing, self.count_of_pages * 10)

        db = DataBase(f'{self.game_for_parsing}')
        db.set_data(data)
