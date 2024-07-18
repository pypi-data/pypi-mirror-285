from ..models import (
    Tick,
    Summary,
    BaseModel,
    Event,
    Order,
    Position,
    Deal,
    Error,
    Symbol,
)
import json
from typing import Tuple, Union
from decimal import Decimal, ROUND_DOWN
import datetime as dt
import time


def deserialize_tick(message: bytes) -> Tick:
    """Deserialize the tick message to a tick object

    Args:
        message (bytes): incoming message from the server

    Returns:
        Tick: a tick object
    """
    splitted = message.decode("utf-8").split(",")
    ID = int(splitted[0])
    Bid = float(splitted[1])
    Ask = float(splitted[2])
    High = float(splitted[3])
    Low = float(splitted[4])
    Close = float(splitted[5])
    Open = float(splitted[6])
    Volume = float(splitted[7])
    Time = int(splitted[8])
    return Tick(
        symbol_id=ID,
        bid=Bid,
        ask=Ask,
        high=High,
        low=Low,
        close=Close,
        open=Open,
        volume=Volume,
        time=Time,
    )


def deserialize_summary(message: str) -> Summary:
    """Deserialize the summary message to a summary object

    Args:
        message (str): incoming message from the server

    Returns:
        Summary: a summary object
    """
    splitted = message.split(",")
    balance = convert_to_float(splitted[1])
    credit = convert_to_float(splitted[2])
    equity = convert_to_float(splitted[3])
    used_margin = splitted[4]
    free_margin = convert_to_float(splitted[5])
    margin_level = splitted[6]

    return Summary(
        balance=balance,
        credit=credit,
        equity=equity,
        used_margin=used_margin,
        free_margin=free_margin,
        margin_level=margin_level,
    )


def deserialize_model(cls: BaseModel, payload: str) -> BaseModel:
    """Deserialize the incoming message to a BaseModel object (cls) using the payload

    Args:
        cls (BaseModel): the class of the object to deserialize to
        payload (str): the incoming message from the server

    Returns:
        BaseModel: the class object after deserialization
    """
    message = json.loads(payload)
    return cls(**message.get("payload"))


def convert_to_float(value: str) -> float:
    """Convert a string to a float

    Args:
        value (str): the string to convert

    Returns:
        float: the float value
    """
    try:
        return float(value)
    except ValueError:
        return 0.0


events_deserializer = {
    Event.ORDER: Order,
    Event.POSITION: Position,
    Event.DEAL: Deal,
    Event.ERROR: Error,
}


def truncate_float(number, digits):
    decimal_number = Decimal(str(number))
    return float(
        decimal_number.quantize(Decimal("1." + "0" * digits), rounding=ROUND_DOWN)
    )


def calculate_spread(symbol: Symbol) -> Tuple[float, float]:
    """Calculate the spread of a symbol

    Args:
        symbol (BaseModel): the symbol object

    Returns:
        Tuple[float, float]: a tuple of the spread for bid and ask
    """
    if symbol is None:
        return 0, 0
    spread_balance = symbol.spread_balance or 0
    spread = symbol.spread or 0
    math_pow = 0
    if symbol.digits is not None:
        math_pow = 10 ** (symbol.digits * -1)

    spread_bid = spread_balance * math_pow
    if symbol.spread is not None:
        spread_ask = (spread_balance + spread) * math_pow
    else:
        spread_ask = spread_balance * math_pow

    return spread_bid, spread_ask


def apply_spread(symbol: Symbol) -> Symbol:
    """Apply the spread to the symbol

    Args:
        symbol (Symbol): the symbol object

    Returns:
        Symbol: the symbol object with the spread applied
    """

    if symbol.spread is None:
        symbol
    else:
        # calculate the spread
        bid_spread, ask_spread = calculate_spread(symbol)
        # apply the spread to the symbol and truncate the digits
        symbol.last_bid = truncate_float(symbol.last_bid + bid_spread, symbol.digits)
        symbol.low_bid = truncate_float(symbol.low_bid + bid_spread, symbol.digits)
        symbol.high_bid = truncate_float(symbol.high_bid + bid_spread, symbol.digits)
        if symbol.spread is not None:
            symbol.low_ask = truncate_float(symbol.low_bid + ask_spread, symbol.digits)
            symbol.high_ask = truncate_float(
                symbol.high_bid + ask_spread, symbol.digits
            )
            symbol.last_ask = truncate_float(
                symbol.last_bid + ask_spread, symbol.digits
            )
        else:
            symbol.low_ask = truncate_float(symbol.low_ask + ask_spread, symbol.digits)
            symbol.high_ask = truncate_float(
                symbol.high_ask + ask_spread, symbol.digits
            )
            symbol.last_ask = truncate_float(
                symbol.last_ask + ask_spread, symbol.digits
            )
        symbol.open = truncate_float(symbol.open + symbol.spread_balance, symbol.digits)
        symbol.close = truncate_float(
            symbol.close + symbol.spread_balance, symbol.digits
        )

    return symbol


def convert_time_to_int(t: Union[int, float, str, dt.datetime]) -> int:
    if isinstance(t, int):
        return t
    if isinstance(t, float):
        return int(t)
    if isinstance(t, str):
        try:
            # if format is yyyy-mm-dd convert it to isoformat
            if len(t) == 10:
                t += "T00:00:00"
            return int(dt.datetime.fromisoformat(t).timestamp())
        except Exception:
            raise ValueError(
                "Invalid time string format, must be in isoformat yyyy-mm-dd"
            )
    if isinstance(t, dt.datetime):
        return int(t.timestamp())
    raise ValueError("Invalid time type")
