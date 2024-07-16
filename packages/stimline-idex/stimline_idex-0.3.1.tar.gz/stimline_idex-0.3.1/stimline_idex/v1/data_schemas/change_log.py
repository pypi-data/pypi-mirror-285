from datetime import datetime
from typing import Optional

from .base import IDEX


class ChangeLog(IDEX):
    id: str
    anchor: int
    type: Optional[str]
    source: Optional[str]
    created_date: Optional[datetime]
