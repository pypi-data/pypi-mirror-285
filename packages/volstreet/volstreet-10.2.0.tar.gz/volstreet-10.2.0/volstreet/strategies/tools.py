from volstreet import config
from volstreet.trade_interface.order_execution import execute_instructions
from volstreet.trade_interface.instruments import Option, Strangle, Straddle, Action

if config.backtest_mode:
    from volstreet.backtests.proxy_functions import execute_instructions


def filter_orders_by_strategy(
    orders: list[dict], strategy_name: str, underlying: str
) -> list[dict]:
    filtered_orders = [
        order
        for order in orders
        if strategy_name.lower() in order.get("ordertag", "").lower()
        and order.get("tradingsymbol").startswith(underlying)
    ]
    return filtered_orders


def execute_single_instrument(
    instrument: Option | Strangle | Straddle,
    action: Action,
    quantity_in_lots: int,
    square_off_order: bool = False,
    order_tag: str = "",
    at_market: bool = False,
):
    instructions = {
        instrument: {
            "action": action,
            "quantity_in_lots": quantity_in_lots,
            "order_tag": order_tag,
            "square_off_order": square_off_order,
        }
    }
    exec_details = execute_instructions(instructions, at_market=at_market)
    exec_price = exec_details[instrument]
    return exec_price
