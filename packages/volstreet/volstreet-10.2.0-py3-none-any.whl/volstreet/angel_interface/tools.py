from datetime import datetime, timedelta


def format_quote_response(response: list) -> list:
    return [
        {
            "token": quote["symbolToken"],
            "ltp": quote["ltp"],
            "best_bid": quote["depth"]["buy"][0]["price"],
            "best_bid_qty": quote["depth"]["buy"][0]["quantity"],
            "best_ask": quote["depth"]["sell"][0]["price"],
            "best_ask_qty": quote["depth"]["sell"][0]["quantity"],
            "timestamp": datetime.strptime(quote["exchFeedTime"], "%d-%b-%Y %H:%M:%S"),
            "last_traded_datetime": datetime.strptime(
                quote["exchTradeTime"], "%d-%b-%Y %H:%M:%S"
            )
            + timedelta(hours=5, minutes=30),
        }
        for quote in response
    ]
