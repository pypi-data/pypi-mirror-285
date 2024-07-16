# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .order import Order
from ..._models import BaseModel

__all__ = ["ExecutionReport", "Fee"]


class Fee(BaseModel):
    asset: Optional[str] = None
    """Asset"""

    quantity: Optional[float] = None
    """Quantity"""


class ExecutionReport(BaseModel):
    base_currency: str = FieldInfo(alias="baseCurrency")
    """Base currency"""

    cost: float
    """Cost, the total cost of the quote"""

    created_at: int = FieldInfo(alias="createdAt")
    """Create time of the quote"""

    filled: float
    """Filled quantity, the quantity of the base currency executed"""

    quote_currency: str = FieldInfo(alias="quoteCurrency")
    """Quote currency"""

    route_policy: Literal["PRIORITY", "QUOTE"] = FieldInfo(alias="routePolicy")
    """Route policy.

    For PRIORITY, the order request will be routed to the exchange account with the
    highest priority. For QUOTE, the system will execute the execution plan based on
    the quote. Order request with route policy QUOTE will only accept two
    parameters, quoteRequestId and priceSlippageTolerance
    """

    status: Literal[
        "SUBMITTED",
        "ACCEPTED",
        "OPEN",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "PENDING_CANCEL",
        "REJECTED",
        "EXPIRED",
        "REVOKED",
    ]
    """
    Status of the quote execution, should only have SUBMITTED, ACCEPTED,
    PARTIALLY_FILLED, FILLED, EXPIRED. the final status of the quote execution
    should be either FILLED or EXPIRED
    """

    updated_at: int = FieldInfo(alias="updatedAt")
    """Last updated time of the quote execution"""

    cl_ord_id: Optional[str] = FieldInfo(alias="clOrdId", default=None)
    """Order request ID, Client Order ID"""

    executions: Optional[List[Order]] = None
    """
    List of executions to fulfill the order, the order status should only have
    FILLED, REJECTED, or EXPIRED
    """

    fees: Optional[List[Fee]] = None
    """Fees"""

    order: Optional[Order] = None
