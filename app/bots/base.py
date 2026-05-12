# bots/base_bot.py

from abc import ABC, abstractmethod
from services import Steam
from services.ASF import ASF

from services.logger import CustomLogger


class BaseBot(ABC):
    def __init__(self, steam: Steam, asf: ASF) -> None:
        self.steam: Steam = steam
        self.asf: ASF = asf
        self.logger: CustomLogger = CustomLogger()

    @abstractmethod
    def process(self):
        pass

    def cancel_order(self, order_id):
        info = 'Ошибка удаления какая то...'
        try:
            info = self.steam.client.market.cancel_buy_order(int(order_id))
            self.logger.info('Order successfully canceled!')
        except Exception as e:
            # import traceback
            # traceback.print_exc()
            # print('Ошибка удаления')
            self.logger.warning(f'WTF? {info}')