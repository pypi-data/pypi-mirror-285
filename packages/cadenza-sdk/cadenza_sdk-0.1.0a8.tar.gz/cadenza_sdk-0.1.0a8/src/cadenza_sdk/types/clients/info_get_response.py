# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["InfoGetResponse"]


class InfoGetResponse(BaseModel):
    exchange_types: Optional[
        List[Literal["BINANCE", "BINANCE_MARGIN", "B2C2", "WINTERMUTE", "BLOCKFILLS", "STONEX"]]
    ] = FieldInfo(alias="exchangeTypes", default=None)
    """Available exchange types"""
