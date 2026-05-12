import json, os

class DataBase:
    def __init__(self, path: str):
        self._path = path
        if not os.path.exists('data/'+path+'.json'):
            self.set_data({})

    def get_data(self) -> dict:
        with open(f"data/{self._path}.json", "r", encoding='utf-8') as file:
            return json.load(fp=file)

    def set_data(self, data: dict):
        with open(f"data/{self._path}.json", 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


def get_item_price_from_total(nTotal: int) -> int:
    # Захардкоженные данные кошелька (как в твоём JS)
    g_rgWalletInfo = {
        "wallet_currency": 5,
        "wallet_country": "RU",
        "wallet_state": "",
        "wallet_fee": "1",
        "wallet_fee_minimum": "75",
        "wallet_fee_percent": "0.05",
        "wallet_publisher_fee_percent_default": "0.10",
        "wallet_market_minimum": "75",
        "wallet_currency_increment": "1",
        "wallet_fee_base": "0",
        "wallet_balance": "392735",
        "wallet_delayed_balance": "0",
        "wallet_max_balance": "17500000",
        "wallet_trade_max_balance": "15750000",
        "success": True,
        "rwgrsn": -2
    }

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


# Пример использования:
# price = GetItemPriceFromTotal(1500)
# print(price)


# Остальные функции (to_valid_market_price, calculate_fee, get_total_with_fees)
# оставь как у тебя — они почти идентичны.
if __name__ == '__main__':
    print(get_item_price_from_total(495))