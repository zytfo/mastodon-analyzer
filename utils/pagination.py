# stdlib
from math import ceil
from typing import Any, Dict


class Pagination:
    def __init__(self, page: int, pages: int, on_page: int, total_results: int) -> None:
        self.page = page
        self.pages = pages
        self.on_page = on_page
        self.total_results = total_results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "pages": self.pages,
            "on_page": self.on_page,
            "total_results": self.total_results,
        }


def calculate_pagination(page: int, limit: int, total_count: int) -> Dict[str, Any]:
    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    pages = ceil(total_count / limit) if total_count > 0 else 1
    on_page = min(limit, total_count - (page - 1) * limit)

    pagination = Pagination(
        page=page,
        pages=pages,
        on_page=on_page,
        total_results=total_count,
    )
    return pagination.to_dict()
