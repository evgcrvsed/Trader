from core.config import SteamAccount, BotSettings, bot_settings, steam_settings
from steampy.models import GameOptions
import time
from bots.base import BaseBot
from utils.functions import *
from services.ignored_item import IgnoredItemService
from schemas.ignored_item import IgnoredItemCreate, IgnoredItemRead

class MarketBot(BaseBot):
    def __init__(self, steam, asf, ignored_item_service):
        super().__init__(steam, asf)
        self.ignored_item_service: IgnoredItemService = ignored_item_service

    def process(self):
         items_no_need_to_remove = []
         items_need_to_remove = []
         items_price = {}
         items_in_sale = {}

         my_listings = self.steam.get_my_market_listings()['sell_listings']
         self.logger.info(f'Проверка лотов на продажу...')
         self.logger.info(f'Лотов: {len(my_listings)}')

         for listing in my_listings:
             # break
             market_hash_name = my_listings[listing]['description']['market_hash_name']
             if market_hash_name in items_no_need_to_remove:
                 self.logger.info(f'Лот: {market_hash_name} имеет актуальную цену!')
                 continue

             self.logger.info(f'Запрашиваем цену: {market_hash_name}')

             if market_hash_name not in items_need_to_remove:
                 try:
                     price = self.steam.get_item_price(
                        appid=my_listings[listing]['description']['appid'],
                        contextid=my_listings[listing]['description']['contextid'],
                        item_hash_name=market_hash_name
                     )
                 except Exception as e:
                     import traceback
                     traceback.print_exc()
                     time.sleep(5)
                     continue
                 finally:
                     time.sleep(5)
             else:
                 self.logger.info('Удалять надо, цену не прогружаем!')
                 price = 0

             my_price = int(float(my_listings[listing]['buyer_pay'].replace(' руб.', '').replace(',', '.').replace(' каждый', '')) * 100)
             lowest_price = int(float(price) * 100)

             if lowest_price <= bot_settings.steam_minimal_price:
                 my_price = 9999999
                 self.logger.info('Предмет дерьма, никто не купит...')

             if my_price > lowest_price:
                 self.logger.info(f'Снимаем с продажи! {my_price}:{lowest_price}')
                 if market_hash_name not in items_need_to_remove:
                     items_need_to_remove.append(market_hash_name)
                 try:
                     self.steam.client.market.cancel_sell_order(my_listings[listing]['listing_id'])
                     time.sleep(5)
                 except Exception as e:
                     import traceback
                     traceback.print_exc()
                     time.sleep(5)
             else:  # Если цена предмета равна моей цене, то оставляем:
                 self.logger.info(f'Предмет и так в топе: {my_price}:{lowest_price}')
                 items_no_need_to_remove.append(market_hash_name)

         for game in [GameOptions.TF2, GameOptions.DOTA2, GameOptions.DST, GameOptions.RUST, GameOptions.STEAM]:
             items = self.steam.get_inventory(game=game)
             self.logger.info(f'Предметов игры {game.app_id} в инвентаре: {len(items)}')
             time.sleep(15)

             for item in items:
                 market_hash_name = items[item]['market_hash_name']
                 if items[item]['marketable'] == 0:
                     self.logger.info(f'Андрейтабл: {market_hash_name}')
                     continue

                 if self.ignored_item_service.get_by_market_hash_name(market_hash_name=market_hash_name) is not None:
                     self.logger.info(f'Игнор: {market_hash_name}')
                     continue

                 # pprint(items[item])

                 try:
                     if market_hash_name not in items_price:
                         self.logger.info(f'Прогрузка цены: {market_hash_name}')
                         price = self.steam.get_item_price(
                             appid=items[item]['appid'],
                             contextid=items[item]['contextid'],
                             item_hash_name=market_hash_name
                         )
                         price = int(float(price) * 100)
                         items_price[market_hash_name] = price
                         time.sleep(5)
                     else:
                         price = items_price[market_hash_name]
                 except Exception as e:
                     import traceback
                     traceback.print_exc()
                     price = 0
                     time.sleep(5)

                 price -= 1

                 price_with_fee = get_item_price_from_total(price)
                 self.logger.info(f'Цена предмета: {price}')
                 self.logger.info(f'Выставляю по {price_with_fee}')

                 if price <= bot_settings.steam_minimal_price:  # ???
                     self.logger.info(f'Не продаём по минималке: {market_hash_name}')
                     self.ignored_item_service.create(IgnoredItemCreate(market_hash_name=market_hash_name))
                     continue

                 # input(price)

                 # continue
                 try:
                     if market_hash_name not in items_in_sale:
                         items_in_sale[market_hash_name] = 0

                     if items_in_sale[market_hash_name] >= 3:
                         self.logger.info(f'Больше трёх не продаём: {market_hash_name}')
                         continue

                     self.steam.client.market.create_sell_order(
                         items[item]['id'],
                         game,
                         str(price_with_fee),
                         int(items[item]['amount'])
                     )
                     items_in_sale[market_hash_name] += 1

                     time.sleep(5)

                     self.asf.auto_confirm(steam_settings.steam_login)
                 except Exception as e:
                     import traceback
                     traceback.print_exc()

