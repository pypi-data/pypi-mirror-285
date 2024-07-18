import dataclasses
from typing import Dict, Any


@dataclasses.dataclass
class MsgMessage:
    """Messaging message model."""

    headers: Dict[str, Any]
    address: str
    body: Dict[str, Any]


@dataclasses.dataclass
class MsgError:
    """Messaging error model."""

    name: str
    description: str
    source: Any
