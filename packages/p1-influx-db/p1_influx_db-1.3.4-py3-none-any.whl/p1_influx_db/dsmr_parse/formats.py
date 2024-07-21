from collections import namedtuple
from pydantic import BaseModel, AwareDatetime
from typing import Dict, Any

dsmrMessages = namedtuple("dsmrMessages", ["topic", "payload"])


class p1Messages(BaseModel):
    measurement: str
    tags: Dict[str, Any]
    fields: Dict[str, Any]
    time: AwareDatetime
