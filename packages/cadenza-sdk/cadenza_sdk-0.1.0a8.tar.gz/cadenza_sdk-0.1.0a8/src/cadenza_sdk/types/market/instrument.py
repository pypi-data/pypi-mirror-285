# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Instrument"]


class Instrument(BaseModel):
    exchange_type: Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"] = FieldInfo(
        alias="exchangeType"
    )
    """Exchange type"""

    symbol: str
    """Symbol name"""

    base_symbol: Optional[str] = FieldInfo(alias="baseSymbol", default=None)
    """Base currency"""

    description: Optional[str] = None
    """Symbol description"""

    margin_rate: Optional[float] = FieldInfo(alias="marginRate", default=None)
    """Margin rate"""

    max_quantity: Optional[float] = FieldInfo(alias="maxQuantity", default=None)
    """Max quantity"""

    min_quantity: Optional[float] = FieldInfo(alias="minQuantity", default=None)
    """Min quantity"""

    min_tick: Optional[float] = FieldInfo(alias="minTick", default=None)
    """Min tick, Price Tick"""

    order_types: Optional[
        List[Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "QUOTED"]]
    ] = FieldInfo(alias="orderTypes", default=None)
    """Supported order types"""

    pip_size: Optional[float] = FieldInfo(alias="pipSize", default=None)
    """Pip size"""

    pip_value: Optional[float] = FieldInfo(alias="pipValue", default=None)
    """Pip value"""

    price_precision: Optional[int] = FieldInfo(alias="pricePrecision", default=None)
    """Price precision"""

    quantity_precision: Optional[int] = FieldInfo(alias="quantityPrecision", default=None)
    """Quantity precision"""

    quantity_step: Optional[float] = FieldInfo(alias="quantityStep", default=None)
    """Quantity step, round lot"""

    quote_symbol: Optional[str] = FieldInfo(alias="quoteSymbol", default=None)
    """Quoted currency"""

    security_type: Optional[
        Literal["SPOT", "CASH", "STOCK", "CRYPTO", "DERIVATIVE", "OPTION", "FUTURE", "FOREX", "COMMODITY"]
    ] = FieldInfo(alias="securityType", default=None)
    """Security type"""

    time_in_force: Optional[
        List[Literal["DAY", "GTC", "GTX", "GTD", "OPG", "CLS", "IOC", "FOK", "GFA", "GFS", "GTM", "MOO", "MOC", "EXT"]]
    ] = FieldInfo(alias="timeInForce", default=None)
    """Supported time in force"""
