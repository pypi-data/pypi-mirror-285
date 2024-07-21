from enum import Enum

class ScreenerValues(Enum):
    ABS = "abs"
    CHG = "chg"

class Lookback(Enum):
    ONE_HOUR = "1H"
    SIX_HOURS = "6H"
    TWELVE_HOURS = "12H"
    ONE_DAY = "1D"
    SEVEN_DAYS = "7D"
    THIRTY_DAYS = "30D"


class EntityType(Enum):
    FINANCIAL_ASSET = "financial_asset"
    COMPANY = "company"
    ORGANIZATION = "organization"
    PERSON = "person"
    PLACE = "place"

class AssetClass(Enum):
    CRYPTO = "crypto"

class SearchMethod(Enum):
    EXACT = "exact"
    CONTAINS = "contains"
    KEYWORD = "keyword"


class NodeMetrics(Enum):
    SENTIMENT = 'sentiment'
    MENTIONS = 'mentions'
    EXCITEMENT = 'excitement'
    OPTIMISM = 'optimism'
    PESSIMISM = 'pessimism'
    FEAR = 'fear'
    UNCERTAINTY = 'uncertainty'
    SURPRISE = 'surprise'
