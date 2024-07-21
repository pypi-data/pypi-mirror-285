from tradex.constants.enuming import Direction, ProfitPossibility
from tradex.constants.listting import TP_FIB, TP_PER_AGGRESSIVE, TP_PER_LOW, TP_PER_MARKET
from tradex.models.order import OrderProfitFormSimple
from tradex.models.take_profit import TakeProfit
from tradex.utils.fibonacci import fib_retrace_standalone


def take_profit_list(
    *, order: OrderProfitFormSimple, tpp: ProfitPossibility | None = ProfitPossibility.MARKET
) -> list[TakeProfit]:
    take_profit_per = None
    if tpp == ProfitPossibility.MARKET:
        take_profit_per = TP_PER_MARKET
    elif tpp == ProfitPossibility.LOW:
        take_profit_per = TP_PER_LOW
    elif tpp == ProfitPossibility.AGGRESSIVE:
        take_profit_per = TP_PER_AGGRESSIVE
    return [
        TakeProfit(
            volume=round(order.size * per, 3),
            price=fib_retrace_standalone(start=order.price, middle=order.middle, fib_val=fib),
        )
        for fib, per in zip(TP_FIB, take_profit_per, strict=False)
    ]


def take_profit_total(*, order: OrderProfitFormSimple, take_profits: list[TakeProfit]) -> float:
    total_price = sum([tp.volume * tp.price for tp in take_profits])
    if order.order_type == Direction.LONG:
        return round(total_price - order.order_price, 2)
    else:  # noqa
        return round(order.order_price - total_price, 2)


# def stop_loss_cal(order: OrderProfitFormSimple,
#                   stop_loss: list[StopLoss]) -> float:
#     total_price = sum([sl.volume * sl.price for sl in stop_loss])
#     return round(order.order_price - total_price, 2)
