# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from .execution_report import ExecutionReport

__all__ = ["QuoteExecutionReport"]


class QuoteExecutionReport(ExecutionReport):
    quote_request_id: str = FieldInfo(alias="quoteRequestId")
    """Quote request ID"""

    valid_until: int = FieldInfo(alias="validUntil")
    """Expiration time of the quote"""
