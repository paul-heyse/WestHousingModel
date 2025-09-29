"""Geometry helpers for distance calculations and coordinate normalization."""

from __future__ import annotations

import math
from dataclasses import dataclass

EARTH_RADIUS_M = 6_371_008.8
_DEGREE_TO_M = 111_320.0


@dataclass(frozen=True)
class Coordinate:
    """Represents a geographic coordinate in decimal degrees."""

    latitude: float
    longitude: float


def haversine_distance_meters(point_a: Coordinate, point_b: Coordinate) -> float:
    """Compute the great-circle distance between two coordinates in meters."""

    lat1 = math.radians(point_a.latitude)
    lat2 = math.radians(point_b.latitude)
    d_lat = lat2 - lat1
    d_lon = math.radians(point_b.longitude - point_a.longitude)

    sin_lat = math.sin(d_lat / 2.0)
    sin_lon = math.sin(d_lon / 2.0)
    a = sin_lat**2 + math.cos(lat1) * math.cos(lat2) * sin_lon**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_M * c


def normalize_coordinate(coordinate: Coordinate, grid_size_m: float = 50.0) -> Coordinate:
    """Snap a coordinate to a grid sized for caching and rate-limit mitigation."""

    if grid_size_m <= 0:
        raise ValueError("grid_size_m must be positive")

    lat_step = grid_size_m / _DEGREE_TO_M
    cos_lat = math.cos(math.radians(coordinate.latitude))
    lon_divisor = max(cos_lat, 1e-6) * _DEGREE_TO_M
    lon_step = grid_size_m / lon_divisor

    lat = round(coordinate.latitude / lat_step) * lat_step
    lon = round(coordinate.longitude / lon_step) * lon_step
    return Coordinate(latitude=lat, longitude=lon)


def bounding_box(center: Coordinate, radius_m: float) -> tuple[Coordinate, Coordinate]:
    """Return a simple bounding box around a coordinate for coarse filtering."""

    if radius_m <= 0:
        raise ValueError("radius_m must be positive")

    lat_delta = radius_m / _DEGREE_TO_M
    cos_lat = math.cos(math.radians(center.latitude))
    lon_delta = radius_m / (max(cos_lat, 1e-6) * _DEGREE_TO_M)
    southwest = Coordinate(center.latitude - lat_delta, center.longitude - lon_delta)
    northeast = Coordinate(center.latitude + lat_delta, center.longitude + lon_delta)
    return southwest, northeast


__all__ = ["Coordinate", "bounding_box", "haversine_distance_meters", "normalize_coordinate"]
