from dataclasses import dataclass, field
from typing import Dict
import collections

@dataclass
class Pad:
    x: float
    y: float
    width: float
    height: float
    rotation: int = 0
    net: str = ""


@dataclass
class Package:
    pads: Dict[str, Pad]


@dataclass
class Element:
    package: Package
    pads: Dict[str, Pad] = field(default_factory=dict)
    x: float = 0.0
    y: float = 0.0
    rotation: int = 0   # angle in degrees
