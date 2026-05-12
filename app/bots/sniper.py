from bots.base import BaseBot
from steampy.models import GameOptions, PredefinedOptions
from utils.functions import DataBase
import random
import time


class States:
    IDLE = 'IDLE'
    SELLING = 'SELLING'
    LISTING = 'LISTING'
    AFK = 'AFK'

class SniperBot(BaseBot):
    def get_price_by_id(self, id):
        try:
            item_data = self.steam.get_item_itemordershistogram(id)
            buy_order = int(item_data.get('highest_buy_order', 0))
            sell_order = int(item_data.get('lowest_sell_order', 9999999))
            kf = round((sell_order - buy_order) / buy_order * 100, 2)
            # self.logger.info(item_data)
            return buy_order, sell_order, kf
        except:
            return 0, 0, 0

    @staticmethod
    def get_game_options(game_id):
        for name, value in vars(GameOptions).items():
            if isinstance(value, PredefinedOptions) and game_id == value.app_id:
                return value
        raise ValueError(f'Неизвестный game_id: {game_id}. Добавьте в GameOptions.')

    def ensure_items_metadata(self, data, db):
        for key in data.keys():
            updated = False
            if 'id' not in data[key]:
                info = self.steam.get_item_id(data[key]['url'])
                data[key]['id'] = info['id']
                data[key]['item_name'] = info['item_name']

                updated = True

                time.sleep(random.uniform(4, 6))  # Ограничение частоты запросов

            if updated:
                db.set_data(data)

        for key in data.keys():
            if 'status' not in data[key]:
                data[key]['status'] = 'IDLE'
            if 'buy_order' not in data[key]:
                data[key]['buy_order'] = '0'
            if 'game_id' not in data[key]:
                data[key]['game_id'] = data[key]['url'].split('/')[-2]
            if 'buy_order_id' not in data[key]:
                data[key]['buy_order_id'] = '0'
            if 'context_id' not in data[key]:
                game = SniperBot.get_game_options(data[key]['game_id'])
                data[key]['context_id'] = game.context_id

        db.set_data(data)


    @staticmethod
    def get_item_name(url: str):
        name = url.split('/')[-1]
        name = name.replace('%20', ' ')
        name = name.replace('%28', '(')
        name = name.replace('%29', ')')
        name = name.replace('%3A', ':')
        name = name.replace('%27', "'")
        name = name.replace('%C3%9C', "Ü")
        name = name.replace('%C3%B1', "ñ")
        name = name.replace('%C3%B2', "ò")
        return name

    @staticmethod
    def is_in_sell_orders(my_sell_orders, market_hash_name):
        for my_sell_order in my_sell_orders:
            if my_sell_orders[my_sell_order]['description']['market_hash_name'] == market_hash_name:
                return True
        return False

    @staticmethod
    def is_in_my_buy_orders(buy_orders, item_name):
        for buy_order in buy_orders:
            if buy_orders[buy_order]['item_name'] == item_name:
                return True
        return False

    def is_in_inventory(self, item):
        for name, value in vars(GameOptions).items():
            if isinstance(value, PredefinedOptions):
                if item['game_id'] == value.app_id:
                    game = value
                    break
        else:
            self.logger.critical('Ебать блять')
            exit(1)

        if game.app_id not in self.inventory:
            self.inventory[game.app_id] = self.steam.get_inventory(game=game)

        inventory = self.inventory[game.app_id]
        # print(inventory)
        for item_inv in inventory:
            if inventory[item_inv]['market_hash_name'] == self.get_item_name(item['url']):
                return True
        return False

    def process(self):
        db = DataBase('sniper')
        db_trash = DataBase('sniper_trash')
        trash = db_trash.get_data()
        data = db.get_data()
        my_buy_orders = self.steam.get_my_market_listings()['buy_orders']
        my_sell_listings = self.steam.get_my_market_listings()['sell_listings']

        buy_orders_len = len(my_buy_orders)

        self.inventory = {}
        self.logger.info(f'Нужно заснайпить предметов: {len(data)}')
        self.ensure_items_metadata(data=data, db=db)
        for item in list(data.keys()):
            is_having = False
            item = data[item]

            if item["status"] == States.AFK:
                self.logger.info(f'Предмет хуйни')
                trash[item['url']] = item
                db_trash.set_data(trash)

                del data[item['url']]
                db.set_data(data)
                continue

            self.logger.info(f'Выбранный предмет: {item}')
            self.logger.info(f'Состояние: {item["status"]}')

            if item["status"] == States.LISTING and str(item["buy_order_id"]) not in my_buy_orders:
                self.logger.info(f'Не нашёл в buy_order: {item["buy_order_id"]}')
                item['status'] = States.IDLE
                item['buy_order_id'] = '0'
                db.set_data(data)

            if item['status'] == States.IDLE:
                self.logger.info(f'Проверка наличия...')
                self.logger.info(self.get_item_name(item["url"]))

                # for order in my_sell_orders:
                #     print(my_sell_orders[order]['description']['market_hash_name'])

                is_having = self.is_in_sell_orders(my_sell_listings, self.get_item_name(item["url"]))
                self.logger.info(f'Продаётся: {is_having}')

                if not is_having:
                    is_having = self.is_in_inventory(item)
                    self.logger.info(f'Наличие в инвентаре: {is_having}')
                # time.sleep(random.uniform(14, 16))

            if is_having:
                self.logger.info(f'Предмет в наличии, надо продавать!')
                continue

            buy_order, sell_order, kf = self.get_price_by_id(item['id'])
            self.logger.info(f'Автобай на маркете: {buy_order}')
            self.logger.info(f'Автобай мой: {item["buy_order"]}')
            self.logger.info(f'Автоселл на маркете {sell_order}')
            self.logger.info(f'KF: {kf}')
            time.sleep(random.uniform(4, 6))

            trash_item = False
            if kf <= 60:
                trash_item = True
                self.logger.info(f'ЕБАТЬ МАЛЕНЬКИЙ КФ: {kf}')

            if buy_order >= 50_000:
                trash_item = True
                self.logger.info(f'СТОИТ ДОРОГО: {buy_order}')

            if sell_order <= 1_000 and kf <= 100:
                trash_item = True
                self.logger.info(f'Дерьмище: {sell_order}')

            if trash_item:
                self.cancel_order(item['buy_order_id'])
                data[item['url']]['status'] = States.AFK
                data[item['url']]['kf'] = kf
                data[item['url']]['buy_order_id'] = '0'
                db.set_data(data)
                continue # типа дальше продажи не будет

            if int(item['buy_order']) < int(buy_order) and item['status'] == States.LISTING:  # если цена предмета при выставлении меньше чем цена макс цена прямо сейчас
                self.logger.warning(f'Суки блять, цену сбили, надо перевыставить...')
                self.cancel_order(item['buy_order_id'])
                buy_orders_len -= 1

                data[item['url']]['status'] = States.IDLE
                data[item['url']]['buy_order_id'] = '0'
                db.set_data(data)
            elif item['status'] == States.LISTING:
                self.logger.info(f'Предмет в топе! db:{data[item["url"]]["buy_order"]}|market:{buy_order}')
                continue

            # Если дошли до сюда то ебать продавать надо

            if buy_orders_len >= 850:
                self.logger.warning('Выставлено 800 автобаев... Лимит...')
                break
            self.logger.info(f'Лотов на продаже: {len(my_buy_orders)}')

            if item['status'] == States.IDLE:
                game = self.get_game_options(item['game_id'])

                buy_info = self.steam.client.market.create_buy_order(
                    market_name=self.get_item_name(item['url']),
                    price_single_item=buy_order + 1,
                    quantity='1',
                    game=game,
                )
                if buy_info['success'] == 1:
                    self.logger.info(f'Выставили автобай за {buy_order}+1!')

                    data[item['url']]['status'] = States.LISTING
                    data[item['url']]['buy_order_id'] = buy_info['buy_orderid']
                    data[item['url']]['buy_order'] = buy_order + 1

                    buy_orders_len += 1
                    db.set_data(data)
                else:
                    self.logger.critical(f'Чёто не удалось автобай сделать блять: {buy_info}')

            # break
