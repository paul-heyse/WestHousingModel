"""Enumerations shared across the West Housing Model domain entities."""

from __future__ import annotations

from enum import Enum


class GeoLevel(str, Enum):
    """Geographic aggregation levels supported by place entities."""

    MSA = "msa"
    COUNTY = "county"
    TRACT = "tract"
    BLOCK_GROUP = "block_group"


class HazardType(str, Enum):
    """Hazard dimensions tracked for properties."""

    FLOOD = "flood"
    WILDFIRE = "wildfire"
    SEISMIC = "seismic"
    WINTER = "winter"
    HEAT = "heat"
    OTHER = "other"


class ScenarioType(str, Enum):
    """High-level scenario categories exposed to the UI."""

    VALUE_ADD = "value_add"
    STABILIZED = "stabilized"


__all__ = ["GeoLevel", "HazardType", "ScenarioType"]
