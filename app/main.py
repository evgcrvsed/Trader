from bots.canceler_lots_bot import CancelerBot
from core.config import steam_settings
import time

from bots.inventory_seller import MarketBot
from bots.game_parser import ParserBot
from bots.sniper import SniperBot

from requests.exceptions import SSLError, ConnectionError

from services.Steam import Steam
from services.ASF import ASF
from services.logger import CustomLogger

from services.ignored_item import IgnoredItemService
from models.base import Base
from db.engine import engine

from schemas.ignored_item import IgnoredItemCreate

from db.session import get_db

logger = CustomLogger()

def main():
    steam = Steam(
        username=steam_settings.STEAM_LOGIN,
        password=steam_settings.STEAM_PASSWORD,
        steamid=steam_settings.STEAM_STEAM_ID,
        shared_secret=steam_settings.STEAM_SHARED_SECRET,
        identity_secret=steam_settings.STEAM_IDENTITY_SECRET,
    )
    steam_balance = steam.auth(new=False)

    Base.metadata.create_all(bind=engine)

    ignored_item_service = IgnoredItemService()
    # ignored_item_service.create(IgnoredItemCreate(market_hash_name='123'))
    # print(ignored_item_service.get_by_market_hash_name(market_hash_name='123'))

    asf = ASF()

    sniper = SniperBot(steam=steam, asf=asf)
    market = MarketBot(steam=steam, asf=asf, ignored_item_service=ignored_item_service)
    parser = ParserBot(steam=steam, asf=asf, game_for_parsing=304930, count_of_pages=900)
    canceler = CancelerBot(steam=steam, asf=asf)
    canceler.process()


    while True:
        try:
            for bot in [market, sniper, parser]:
                bot.process()
        except SSLError:
            logger.exception("SSLError")
        except ConnectionError:
            logger.exception("ConnectionError")

        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("КРАШНУЛСЯ В ЦИКЛЕ!")
        time.sleep(30 * 60)