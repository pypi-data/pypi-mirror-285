# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import Enum


class FinCoreCategory(Enum):
    MARKET="market"
    ECONOMY="economy"
    POLITICS="poltcs"
    CORPORATE="corp"
    FUNDAMENTAL="fundam"
    SENTIMENT="sntmnt"
    NEWS="news"
    SOCIAL="social"
    OTHER="other"

class FincCoreSubCategory(Enum):
    STOCKS = "stocks"
    BONDS = "bonds"
    COMMODITIES = "cmmdt"
    CURRENCIES = "crrncy"
    CRYPTOCURRENCIES = "crypto"
    REAL_ESTATE = "realest"
    EQUITY_INDICES = "eqindx"
    OPTIONS = "options"
    FUTURES = "futures"
    ETF = "etf"
    ECONOMIC_INDICATORS = "ecoind"
    FUNDAMENTALS = "fundam"
    OTHER = "othr"

class FinCoreRecordsCategory(Enum):
    PRICE="pric"
    PRICE_SPOT= "pric.s"
    PRICE_OHLCVA="pric.ohlcva"
    PRICE_OHLCV="pric.ohlcv"
    PRICE_OPEN="pric.o"
    PRICE_HIGH="pric.h"
    PRICE_LOW="pric.l"
    PRICE_CLOSE="pric.c"
    PRICE_VOLUME="pric.v"
    PRICE_ADJC="pric.a"
    FUNDAMENTAL="fundam" # treat this differently 
    EARNINGS="earnings"
    CASH_FLOW="cashflw"
    BALANCE_SHEET="blnce_sht"
    INTERNAL_TRANSACTIONS="internaltrans"
    INDICATORS="indic"
    ARTICLE="article"
    INSTA_POST="isntapost"
    TWEET="tweet"
    OTHER="othr"

class ExchangeOrPublisher(Enum):
    CC="cc"
    US="us"
    NASDAQ="nasdaq"