from .core.tdObject import tdElement
from playwright.sync_api._generated import ElementHandle, Page

__all__ = ['timeout', 'findElement']

timeout: int

def findElement(selectorString: str, fromElement: tdElement | Page | ElementHandle, timeout: int = None) -> tdElement: ...
