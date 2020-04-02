from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class Layer(Enum):
    TOP = 1
    BOTTOM = 2


@dataclass
class Pad:
    x: float = 0.0
    y: float = 0.0
    length: float = 0.0
    width: float = 0.0
    rotation: int = 0
    layer: Layer = Layer.TOP


@dataclass
class SMDPad(Pad):
    width: float = 0.0
    net: str = ""


@dataclass
class ViaPad(Pad):
    drill: float = 0.0


@dataclass
class Package:
    smd_pads: Dict[str, SMDPad]
    via_pads: Dict[str, ViaPad]


@dataclass
class Element:
    package: Package
    smd_pads: Dict[str, SMDPad] = field(default_factory=dict)
    via_pads: Dict[str, ViaPad] = field(default_factory=dict)
    x: float = 0.0
    y: float = 0.0
    rotation: int = 0  # angle in degrees
