"""
title = "Map Projections - A Working Manual",
editor = "UNITED STATES GOVERNMENT PRINTING OFFICE, WASHINGTON",
year = 1987,
url = "https://pubs.usgs.gov/pp/1395/report.pdf"
section 7, page 38
"""

from typing import override

from math import cos

from coord_operation.operation import InvertibleProjection
from coord_operation.projection import map_projections
from coord_operation.surface import Spheroid


class MercatorSpherical(InvertibleProjection[Spheroid]):
    """The mercator spherical projection as defined in Map Projections."""

    _LATITUDE: int = 0
    _LONGITUDE: int = 1
    _X: int = 0
    _Y: int = 1

    def __init__(self, spheroid: Spheroid, phi0: float, lambda0: float):
        self._spheroid = spheroid
        self._r = spheroid.r()
        self._phi0 = phi0
        self._cos_phi1 = cos(phi0)
        self._lambda0 = lambda0

    @override
    def get_surface(self) -> Spheroid:
        return self._spheroid

    @override
    def compute(self, i):
        return map_projections.x_7_1(self._r, self._cos_phi1, self._lambda0, i[MercatorSpherical._LONGITUDE]), \
               map_projections.y_7_2(self._r, self._cos_phi1, i[MercatorSpherical._LATITUDE])

    @override
    def inverse(self, i):
        return map_projections.phi_7_4(self._r, self._cos_phi1, i[MercatorSpherical._Y]), \
               map_projections.lambda_7_5(self._r, self._cos_phi1, self._lambda0, i[MercatorSpherical._X])
