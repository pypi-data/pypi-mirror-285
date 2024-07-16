# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Generic, TypeVar, Optional
from typing_extensions import override

from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = ["SyncOffset", "AsyncOffset"]

_T = TypeVar("_T")


class SyncOffset(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    data: List[_T]
    offset: Optional[int] = None
    limit: Optional[int] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        offset = self.offset
        if offset is None:
            return None

        length = len(self._get_page_items())
        current_count = offset + length

        return PageInfo(params={"offset": current_count})


class AsyncOffset(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    data: List[_T]
    offset: Optional[int] = None
    limit: Optional[int] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        offset = self.offset
        if offset is None:
            return None

        length = len(self._get_page_items())
        current_count = offset + length

        return PageInfo(params={"offset": current_count})
