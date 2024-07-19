import uiautomation as auto
from .core.tdObject import tdElement

__all__ = ['timeout', 'findElement']

timeout: int

def findElement(selectorString: str = None, fromElement: tdElement | auto.Control = None, timeout: int = None) -> tdElement: ...
