import logging
from typing import Dict

loggers: Dict[str, logging.Logger]

def getLogger(name: str) -> logging.Logger: ...
