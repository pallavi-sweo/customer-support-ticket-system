from dataclasses import dataclass


@dataclass(frozen=True)
class Page:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def normalize_pagination(page: int, page_size: int, max_page_size: int = 50) -> Page:
    page = max(1, page)
    page_size = max(1, min(page_size, max_page_size))
    return Page(page=page, page_size=page_size)
