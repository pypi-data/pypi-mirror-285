import datetime
import enum
from _decimal import Decimal
from dataclasses import dataclass
from typing import Union


class Period(enum.Enum):
    MINUTE = "minute"
    MINUTE_5 = "minute_5"
    MINUTE_15 = "minute_15"
    MINUTE_30 = "minute_30"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class TradingSchedule(enum.Enum):
    PRE_MARKET = "pre_market"
    REGULAR_MARKET = "regular_market"
    AFTER_MARKET = "after_market"
    CLOSED = "closed"


class OptionType(enum.Enum):
    CALL = "call"
    PUT = "put"


class OptionStyle(enum.Enum):
    CALL = "american"
    PUT = "european"


class OptionSettlementType(enum.Enum):
    PHYSICAL = "physical"
    CASH = "cash"


@dataclass
class Quote:
    """
    Quote for the specified symbol.

    Attributes:
        symbol: The security symbol
        ask: Ask price
        ask_size: Ask size
        bid: Bid price
        bid_size: Bid size
        last: Last price
        last_size: Last trade size
        volume: Today total volume
        date: Last trade time
        high: Today's high price
        low: Today's low price
        open: Open price
        close: Yesterday's close price
        week52_high: 52-week high
        week52_low: 52-week low
        change: Today's price change
        change_pc: Today's percent price change
        open_interest: Open interest (options)
        implied_volatility: Implied volatility (options)
        theoretical_price: Theoretical price (options)
        delta: Delta value (options)
        gamma: Gamma value (options)
        theta: Theta value (options)
        vega: Vega value (options)
        rho: Rho value (options)
    """
    symbol: str
    ask: Decimal
    ask_size: Decimal
    bid: Decimal
    bid_size: Decimal
    last: Decimal
    last_size: Decimal
    volume: int
    date: datetime.datetime
    high: Decimal
    low: Decimal
    open: Decimal
    close: Decimal
    week52_high: Decimal
    week52_low: Decimal
    change: Decimal
    change_pc: Decimal
    implied_volatility: Union[Decimal, None] = None
    open_interest: Union[Decimal, None] = None
    theoretical_price: Union[Decimal, None] = None
    delta: Union[Decimal, None] = None
    gamma: Union[Decimal, None] = None
    theta: Union[Decimal, None] = None
    vega: Union[Decimal, None] = None
    rho: Union[Decimal, None] = None


@dataclass
class QuoteHistory:
    timestamp: datetime.datetime
    period: Period
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass
class CurrentSchedule:
    """Trading session info depending on current date and time

    Attributes:
        session: Current session info
    """

    session: TradingSchedule


@dataclass
class Security:
    """Represents security

    Attributes:
        symbol: Security symbol
        description: Description of security
    """

    symbol: str
    description: str


@dataclass
class SecuritiesPage:
    """Page of securities

    Attributes:
        trades: List of securities
        count: Total count of securities
    """

    trades: list[Security]
    count: int

    @property
    def securities(self) -> list[Security]:
        """
        Alias for returned list as API returns it as "trades". Should be used instead of "trades" attribute.

        Returns:
            List of securities
        """
        return self.trades


@dataclass
class Trade:
    timestamp: int
    quantity: int
    price: Decimal
    market: str


@dataclass
class TradesPage:
    """Represents one page of trades

    Attributes:
        trades: List of trades
        count: Total count of trades
    """

    trades: list[Trade]
    count: int


@dataclass(frozen=True)
class OptionSeries:
    """
    Represents option series for the security

    Attributes:
        series: Option series
        expirations: Array of expiration dates
        contract_size: Contract size value
    """
    series: str
    expirations: list[datetime.date]
    contract_size: Decimal


@dataclass(frozen=True)
class OptionContract:
    """
    Single option contract for the security

    Attributes:
        symbol: Option symbol
        type: Option type
        strike: Option strike value
    """
    symbol: str
    type: OptionType
    strike: Decimal


@dataclass(frozen=True)
class OptionChain:
    """
    Option contracts for specified symbol, expiration date and series

    Attributes:
        contract_size: Contract size value
        style: Option style
        settlement: Settlement type
        chain: Array of option contracts
    """
    contract_size: Decimal
    style: OptionStyle
    settlement: OptionSettlementType
    chain: list[OptionContract]
