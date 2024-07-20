
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

from enum import Enum


class NoticeManagerCategory(Enum):
    NOTICES = "notices"
    WARN_ERRS = "warn_errs"
    SUCCESSES = "successes"
class NoticeLevel(Enum):
    """
    Standardized notice levels for data engineering pipelines,
    designed for easy analysis and identification of manual 
    intervention needs.
    """
    DEBUG = 100  # Detailed debug information (for development/troubleshooting)

    INFO = 200

    SUCCESS = 300  # Events requiring attention, but not necessarily errors

     # Warnings indicate potential issues that might require attention:
    WARNING = 400 # General warning, no immediate action required
    WARNING_NO_ACTION = 401 # Minor issue or Unexpected Behavior, no immediate action required (can be logged frequently)
    WARNING_REVIEW_RECOMMENDED = 402 # Action recommended to prevent potential future issues
    WARNING_FIX_RECOMMENDED = 403 # Action recommended to prevent potential future issues
    WARNING_FIX_REQUIRED = 404  # Action required, pipeline can likely continue

    ERROR = 500 # General error, no immediate action required
    # Errors indicate a problem that disrupts normal pipeline execution:
    ERROR_EXCEPTION_REDO = 501
    ERROR_CUSTOM_REDO = 502 # Temporary error, automatic retry likely to succeed
    
    ERROR_EXCEPTION_INVESTIGATE = 601 # Exception occured after some data was likely persisted (e.g., to GCS or BQ)
    ERROR_CUSTOM_INVESTIGATE= 602
    ERROR_EXCEPTION_PERSTISTANCE = 603 # Exception occured after data was persisted (e.g., to GCS or BQ)
    ERROR_CUSTOM_PERSTISTANCE = 604

    # Critical errors indicate severe failures requiring immediate attention:
    CRITICAL_SYSTEM_FAILURE = 701 # System-level failure (e.g., infrastructure), requires immediate action
    CRITICAL_PIPELINE_FAILURE = 702 # Complete pipeline failure, requires investigation and potential rollback

    UNKNOWN=1001 # Unknown error, should not be used in normal operation


class NoticeStatus(Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    IGNORED = "ignored"
  



### Exception during full exection, partially saved
# Exception during ensemble pipeline; modifications collected in local object , nothing persisted
# Exception during ensemble pipeline; modifications persisted , metadata failed
# Exception during ensemble pipeline; modifications persisted , metadata persisted
# Exception during ensemble pipeline; modifications persisted , metadata persisted


class Unit(Enum):
    MIX="MIX"
    # Currency and Financial Values
    USD = "USD"  # United States Dollar
    EUR = "EUR"  # Euro
    JPY = "JPY"  # Japanese Yen
    GBP = "GBP"  # British Pound Sterling
    AUD = "AUD"  # Australian Dollar
    CAD = "CAD"  # Canadian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan Renminbi
    SEK = "SEK"  # Swedish Krona
    NZD = "NZD"  # New Zealand Dollar
    MXN = "MXN"  # Mexican Peso
    SGD = "SGD"  # Singapore Dollar
    HKD = "HKD"  # Hong Kong Dollar
    NOK = "NOK"  # Norwegian Krone
    KRW = "KRW"  # South Korean Won
    RUB = "RUB"  # Russian Ruble
    INR = "INR"  # Indian Rupee
    BRL = "BRL"  # Brazilian Real
    ZAR = "ZAR"  # South African Rand
    CURRENCY = "currency"    # General currency, when specific currency is not needed

    # Stock Market and Investments
    SHARES = "shars"        # Number of shares
    PERCENT = "prcnt"      # Percentage, used for rates and ratios
    BPS = "bps"              # Basis points, often used for interest rates and financial ratios

    # Volume and Quantitative Measurements
    VOLUME = "vol"        # Trading volume in units
    MILLIONS = "mills"    # Millions, used for large quantities or sums
    BILLIONS = "bills"    # Billions, used for very large quantities or sums

    # Commodity Specific Units
    BARRELS = "barrls"      # Barrels, specifically for oil and similar liquids
    TONNES = "tonnes"        # Tonnes, for bulk materials like metals or grains
    TROY_OUNCES = "troy_oz" # Troy ounces, specifically for precious metals

    # Real Estate and Physical Properties
    SQUARE_FEET = "sq_ft"    # Square feet, for area measurement in real estate
    METER_SQUARE = "m2"      # Square meters, for area measurement in real estate
    ACRES = "acres"          # Acres, used for measuring large plots of land

    # Miscellaneous and Other Measures
    UNITS = "units"          # Generic units, applicable when other specific units are not suitable
    COUNT = "count"          # Count, used for tallying items or events
    INDEX_POINTS = "index_pnts"  # Index points, used in measuring indices like stock market indices
    RATIO = "ratio"          # Ratio, for various financial ratios

class Frequency(Enum):
    ONE_MIN = "1min"
    FIVE_MIN="5min"
    FIFTEEN_MIN="15min"
    THIRTY_MIN = "30min"
    ONE_H = "1h"
    TWO_H = "2h"
    SIX_H = "6h"
    TWELVE_H = "12h"
    FOUR_H = "4h"
    EOD="eod"
    ONE_D = "1d"
    TWO_D = "2d"
    THREE_D = "3d"
    ONE_W = "1w"
    ONE_M = "1m"
    TWO_M="2m"
    THREE_M="3m"
    SIX_M="6m"
    ONE_Y="1y"
    THREE_Y="3y"