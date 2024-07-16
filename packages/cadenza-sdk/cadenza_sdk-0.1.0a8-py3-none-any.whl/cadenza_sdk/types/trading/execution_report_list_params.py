# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ExecutionReportListParams"]


class ExecutionReportListParams(TypedDict, total=False):
    end_time: Annotated[int, PropertyInfo(alias="endTime")]
    """End time (in unix milliseconds)"""

    limit: int
    """Limit the number of returned results."""

    offset: int
    """Offset of the returned results. Default: 0"""

    quote_request_id: Annotated[str, PropertyInfo(alias="quoteRequestId")]
    """Quote Request ID"""

    start_time: Annotated[int, PropertyInfo(alias="startTime")]
    """Start time (in unix milliseconds)"""
