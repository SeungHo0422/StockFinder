from .market_cap import MarketCapFilter
from .pe_ratio import PERatioFilter
from .industry import IndustryFilter

FILTERS = [
    MarketCapFilter(),
    PERatioFilter(),
    IndustryFilter(),
] 