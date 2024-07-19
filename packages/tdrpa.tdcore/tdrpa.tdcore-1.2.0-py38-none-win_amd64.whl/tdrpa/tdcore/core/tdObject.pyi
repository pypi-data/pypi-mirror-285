from typing import Union

import uiautomation
from playwright.sync_api._generated import ElementHandle


class tdElement:
    _element: Union[uiautomation.Control,ElementHandle]