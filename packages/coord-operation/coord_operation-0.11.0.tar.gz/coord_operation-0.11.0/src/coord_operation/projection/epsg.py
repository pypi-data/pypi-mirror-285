"""The EPSG projection definitions."""
from enum import Enum, auto
from typing import override

from math import log, tan, pi, atan, exp, sqrt, sin, cos, asin, atan2, degrees, floor

from coord_operation.math_util.integral import sum_function
from coord_operation.operation import InvertibleProjection
from coord_operation.projection.mercator_spherical import MercatorSpherical
from coord_operation.surface import Surface, Spheroid, Ellipsoid


class Epsg1024(InvertibleProjection[Surface]):
    """EPSG::1024
    Popular Visualisation Pseudo-Mercator ("Web Mercator")
    """

    _PHI: int = 0
    _LAMBDA: int = 1
    _EASTING: int = 0
    _NORTHING: int = 1

    def __init__(self, surface: Surface, lambda0: float, fe: float, fn: float):
        self._surface = surface
        self._a = surface.semi_major_axis()
        self._lambda0 = lambda0
        self._fe = fe
        self._fn = fn

    @override
    def get_surface(self) -> Surface:
        return self._surface

    @override
    def compute(self, i):
        return self._fe + self._a * (i[Epsg1024._LAMBDA] - self._lambda0), \
            self._fn + self._a * log(tan(pi / 4. + i[Epsg1024._PHI] / 2.))

    @override
    def inverse(self, i):
        return pi / 2. - 2. * atan(exp((self._fn - i[Epsg1024._NORTHING]) / self._a)), \
            (i[Epsg1024._EASTING] - self._fe) / self._a + self._lambda0


class Epsg1026(MercatorSpherical):
    """EPSG::1026
    Mercator (Spherical)
    """

    _EASTING: int = 0
    _NORTHING: int = 1

    def __init__(self, spheroid: Spheroid, phi0: float, lambda0: float, fe: float, fn: float):
        super().__init__(spheroid=spheroid, phi0=phi0, lambda0=lambda0)
        self._fe = fe
        self._fn = fn

    @override
    def compute(self, i):
        output = super().compute(i)
        return self._fe + output[Epsg1026._EASTING], self._fn + output[Epsg1026._NORTHING]

    @override
    def inverse(self, i):
        return super().inverse([i[Epsg1026._EASTING] - self._fe, i[Epsg1026._NORTHING] - self._fn])


class Epsg1027(InvertibleProjection[Spheroid]):
    """EPSG::1027
    Lambert Azimuthal Equal Area
    """

    class _Aspect(Enum):
        OBLIQUE = auto()
        NORTH_POLE = auto()
        SOUTH_POLE = auto()

    _PHI: int = 0
    _LAMBDA: int = 1
    _EASTING: int = 0
    _NORTHING: int = 1

    def __init__(self, spheroid: Spheroid, phi0: float, lambda0: float, fe: float, fn: float):
        self._spheroid = spheroid
        if abs(phi0 - pi / 2.) < 1e-9:
            self._aspect = Epsg1027._Aspect.NORTH_POLE
        elif abs(phi0 + pi / 2.) < 1e-9:
            self._aspect = Epsg1027._Aspect.SOUTH_POLE
        else:
            self._aspect = Epsg1027._Aspect.OBLIQUE
        self._r = spheroid.r()
        self._phi0 = phi0
        self._lambda0 = lambda0
        self._fe = fe
        self._fn = fn

    @override
    def get_surface(self) -> Spheroid:
        return self._spheroid

    @override
    def compute(self, i):
        phi = i[Epsg1027._PHI]
        r_lambda = i[Epsg1027._LAMBDA] - self._lambda0

        if self._aspect == Epsg1027._Aspect.OBLIQUE:

            rkp = self._r * sqrt(2. / (1. + sin(self._phi0)
                                       * sin(phi) + cos(self._phi0) * cos(phi) * cos(r_lambda)))

            return self._fe + rkp * cos(phi) * sin(r_lambda), \
                self._fn + rkp * (cos(self._phi0) * sin(phi) - sin(self._phi0) * cos(phi) * cos(r_lambda))

        north = self._aspect == Epsg1027._Aspect.NORTH_POLE

        return (self._fe + 2. * self._r * sin(r_lambda)
                * (sin(pi / 4. - phi / 2.) if north else cos(pi / 4. - phi / 2.))), \
            (self._fn + 2. * self._r * cos(r_lambda)
             * (-sin(pi / 4. - phi / 2.) if north else cos(pi / 4. - phi / 2.)))

    @override
    def inverse(self, i):
        easting = i[Epsg1027._EASTING]
        northing = i[Epsg1027._NORTHING]

        east = easting - self._fe
        north = northing - self._fn
        rho = sqrt(east * east + north * north)

        if rho < 1e-9:
            return self._phi0, self._lambda0

        c = 2. * asin(rho / (2. * self._r))
        sinc = sin(c)
        cosc = cos(c)
        phi = asin(cosc * sin(self._phi0) + north * sinc * cos(self._phi0) / rho)

        match self._aspect:
            case Epsg1027._Aspect.NORTH_POLE:
                return phi, self._lambda0 + atan2(easting - self._fe, self._fn - northing)
            case Epsg1027._Aspect.SOUTH_POLE:
                return phi, self._lambda0 + atan2(easting - self._fe, northing - self._fn)
            case Epsg1027._Aspect.OBLIQUE:
                return phi, \
                    self._lambda0 + atan2(east * sinc, rho * cos(self._phi0) * cosc - north * sin(self._phi0) * sinc)


class Epsg1028(InvertibleProjection[Ellipsoid]):
    """Abstract EPSG::1028 projection."""

    _PHI: int = 0
    _LAMBDA: int = 1
    _EASTING: int = 0
    _NORTHING: int = 1

    def __init__(self, ellipsoid: Ellipsoid, phi1: float, lambda0: float, fe: float, fn: float):
        self._ellipsoid = ellipsoid
        self._phi1 = phi1
        self._lambda0 = lambda0
        self._fe = fe
        self._fn = fn

        self._a = ellipsoid.a()
        self._e2 = ellipsoid.e2()
        self._nu1 = ellipsoid.nu(phi1)
        e2 = self._e2
        self._mud = self._a * (1.
                               - e2 * (1. / 4.
                                       + e2 * (3. / 64.
                                               + e2 * (5. / 256.
                                                       + e2 * (175. / 16384.
                                                               + e2 * (441. / 65536.
                                                                       + e2 * (4851. / 1048576.
                                                                               + e2 * 14157. / 4194304.)))))))
        self._n = (1. - sqrt(1. - e2)) / (1. + sqrt(1. - e2))

        n2 = self._n ** 2
        self._f1 = 3. / 2. + n2 * (-27. / 32. + n2 * (269. / 512. - n2 * 6607 / 24576))
        self._f2 = 21. / 16. + n2 * (-55. / 32. + n2 * 6759. / 4096.)
        self._f3 = 151. / 96. + n2 * (-417. / 128 + n2 * 87963. / 20480.)
        self._f4 = 1097. / 512. - n2 * 15543. / 2560.
        self._f5 = 8011. / 2560. - n2 * 69119. / 6144.
        self._f6 = 293393. / 61440.
        self._f7 = 6845701. / 860160.

    @override
    def get_surface(self) -> Ellipsoid:
        return self._ellipsoid

    def m(self, phi: float) -> float:
        """m"""

    @override
    def compute(self, i):
        return self._fe + self._nu1 * cos(self._phi1) * (i[Epsg1028._LAMBDA] - self._lambda0), \
            self._fn + self.m(i[Epsg1028._PHI])

    @override
    def inverse(self, i):
        easting = i[Epsg1028._EASTING]
        northing = i[Epsg1028._NORTHING]

        x = easting - self._fe
        y = northing - self._fn

        mu = y / self._mud

        return self._f(mu), self._lambda0 + x / (self._nu1 * cos(self._phi1))

    def _f(self, m: float) -> float:
        n = self._n
        return m + n * (self._f1 * sin(2. * m)
                        + n * (self._f2 * sin(4. * m)
                               + n * (self._f3 * sin(6. * m)
                                      + n * (self._f4 * sin(8. * m)
                                             + n * (self._f5 * sin(10. * m)
                                                    + n * (self._f6 * sin(12. * m)
                                                           + n * self._f7 * sin(14. * m)))))))


class Epsg1028Series(Epsg1028):
    """EPSG::1028 implementation using series."""

    def __init__(self, ellipsoid: Ellipsoid, phi1: float, lambda0: float, fe: float, fn: float):
        super().__init__(ellipsoid, phi1, lambda0, fe, fn)

        e2 = self._e2
        self._m1 = (1.
                    - e2 * (1. / 4.
                            + e2 * (3. / 64.
                                    + e2 * (5. / 256.
                                            + e2 * (175. / 16384.
                                                    + e2 * (441. / 65536.
                                                            + e2 * (4851. / 1048576.
                                                                    + e2 * 14157. / 4194304.)))))))
        self._m2 = -(3. / 8.
                     + e2 * (3. / 32.
                             + e2 * (45. / 1024.
                                 + e2 * (105. / 4096.
                                     + e2 * (2205. / 131072.
                                             + e2 * (6237. / 524288.
                                                     + e2 * 297297. / 33554432.))))))
        self._m3 = (15. / 256.
                    + e2 * (45. / 1024.
                            + e2 * (525. / 16384.
                                    + e2 * (1575. / 65536.
                                            + e2 * (155925. / 8388608.
                                                    + e2 * 495495. / 33554432.)))))
        self._m4 = -(35. / 3072
                     + e2 * (175. / 12288.
                             + e2 * (3675. / 262144.
                                     + e2 * (13475. / 1048576.
                                             + e2 * 385385. / 33554432.))))
        self._m5 = 315. / 131072. + e2 * (2205. / 524288. + e2 * (43659. / 8388608. + e2 * 189189. / 33554432.))
        self._m6 = -(693. / 1310720. + e2 * (6237. / 5242880. + e2 * 297297. / 167772160.))
        self._m7 = 1001. / 8388608. + e2 * 11011. / 33554432.
        self._m8 = -6435. / 234881024

    @override
    def m(self, phi: float):
        e2 = self._e2
        return self._a * (self._m1 * phi
                          + e2 * (self._m2 * sin(2. * phi)
                                  + e2 * (self._m3 * sin(4. * phi)
                                          + e2 * (self._m4 * sin(6. * phi)
                                                  + e2 * (self._m5 * sin(8. * phi)
                                                          + e2 * (self._m6 * sin(10. * phi)
                                                                  + e2 * (self._m7 * sin(12. * phi)
                                                                          + e2 * self._m8 * sin(14. * phi))))))))


class Epsg1028Integration2dKind(Epsg1028):
    """EPSG::1028 implementation using elliptic integral of the 2d kind."""

    @override
    def m(self, phi: float) -> float:
        return self._a * (sum_function(lambda p: sqrt(1. - self._e2 * sin(p) * sin(p)),
                                       start=0.,
                                       end=phi,
                                       parts=floor(4. * degrees(phi)) + 1)
                          - self._e2 * sin(phi) * cos(phi) / self.get_surface().e_sin_sqrt(phi))


class Epsg1028Integration3rdKind(Epsg1028):
    """EPSG::1028 implementation using elliptic integral of the 3rd kind."""

    @override
    def m(self, phi: float) -> float:
        return self._a * (1 - self._e2) * (sum_function(lambda p: pow(1. - self._e2 * sin(p) * sin(p), -3. / 2.),
                                                        start=0.,
                                                        end=phi,
                                                        parts=floor(50. * degrees(phi)) + 1))


class Epsg1029(InvertibleProjection[Surface]):
    """EPSG::1029

    Equidistant Cylindrical (Spherical)

    See method code 1028 for ellipsoidal development. If the latitude of natural origin is at the equator, also known as
    Plate Carrée. See also Pseudo Plate Carree, method code 9825.
    """

    _PHI = 0
    _LAMBDA = 1
    _EASTING = 0
    _NORTHING = 1

    def __init__(self, surface: Surface, phi1: float, lambda0: float, fe: float, fn: float):
        self._surface = surface
        self._phi1 = phi1
        self._lambda0 = lambda0
        self._fe = fe
        self._fn = fn

        if isinstance(surface, Spheroid):
            self._r = surface.r()
        elif isinstance(surface, Ellipsoid):
            self._r = surface.rc(phi1)
        else:
            raise ValueError

    @override
    def compute(self, i):
        return (self._fe + self._r * (i[Epsg1029._LAMBDA] - self._lambda0) * cos(self._phi1),
                self._fn + self._r * i[Epsg1029._PHI])

    @override
    def inverse(self, i):
        return ((i[Epsg1029._NORTHING] - self._fn) / self._r,
                self._lambda0 + (i[Epsg1029._EASTING] - self._fe) / self._r / cos(self._phi1))

    @override
    def get_surface(self):
        return self._surface


class Epsg9819a(InvertibleProjection[Ellipsoid]):
    """EPSG:9819

    Krovak
    """

    _PHI = 0
    _LAMBDA = 1
    _EASTING = 0
    _NORTHING = 1
    _PRECISION = 1e-12

    def __init__(self,
                 ellipsoid: Ellipsoid,
                 phic: float,
                 lambda0: float,
                 alphac: float,
                 phip: float,
                 kp: float,
                 fe: float,
                 fn: float):
        self._ellipsoid = ellipsoid
        self._a = ellipsoid.a()
        self._e = ellipsoid.e()
        self._phic = phic
        self._lambda0 = lambda0
        self._alphac = alphac
        self._phip = phip
        self._kp = kp
        self._fe = fe
        self._fn = fn

        self._e2 = self._e ** 2
        self._coef_a = self._compute_a()
        self._coef_b = self._compute_b()
        self._g0 = self._compute_g0()
        self._t0 = self._compute_t0()
        self._n = self._compute_n()
        self._r0 = self._compute_r0()

    @override
    def get_surface(self) -> Ellipsoid:
        return self._ellipsoid

    @override
    def compute(self, i):
        u = self._compute_u(i[Epsg9819a._PHI])
        v = self._compute_v(i[Epsg9819a._LAMBDA])
        t = self._compute_t(u, v)
        r = self._r(u, v, t)
        theta = self._theta(u, v, t)
        return r * cos(theta) + self._fn, r * sin(theta) + self._fe

    @override
    def inverse(self, i):
        i_xp = self._compute_inv_xp(i[Epsg9819a._EASTING])
        i_yp = self._compute_inv_yp(i[Epsg9819a._NORTHING])
        i_t = self._compute_inv_t(i_xp, i_yp)
        i_d = self._compute_inv_d(i_xp, i_yp)
        i_u = self._compute_inv_u(i_t, i_d)
        return self._compute_phi(i_u), self._compute_lambda(i_t, i_d, i_u)

    def _compute_a(self) -> float:
        return self._a * sqrt(1. - self._e2) / (1. - self._e2 * sin(self._phic) ** 2)

    def _compute_b(self) -> float:
        return sqrt(1. + self._e2 * cos(self._phic) ** 4 / (1 - self._e2))

    def _compute_u(self, f: float) -> float:
        esinf = self._e * sin(f)
        return 2. * (atan2(self._t0 * pow(tan(f / 2. + pi / 4.), self._coef_b),
                           pow((1. + esinf) / (1. - esinf), self._e * self._coef_b / 2.)) - pi / 4.)

    def _compute_v(self, l: float) -> float:
        return self._coef_b * (self._lambda0 - l)

    def _compute_t(self, u: float, v: float) -> float:
        return asin(cos(self._alphac) * sin(u) + sin(self._alphac) * cos(u) * cos(v))

    def _compute_d(self, u: float, v: float, t: float) -> float:
        return asin(cos(u) * sin(v) / cos(t))

    def _theta(self, u: float, v: float, t: float) -> float:
        return self._n * self._compute_d(u, v, t)

    def _r(self, u: float, v: float, t: float) -> float:
        return self._r0 * pow(tan(pi / 4. + self._phip / 2.) / tan(t / 2. + pi / 4.), self._n)

    def _compute_g0(self) -> float:
        return asin(sin(self._phic) / self._coef_b)

    def _compute_t0(self) -> float:
        sinphic = sin(self._phic)
        return tan(pi / 4. + self._g0 / 2.) \
            * pow((1. + self._e * sinphic) / (1. - self._e * sinphic), self._e * self._coef_b / 2.) \
            / pow(tan(pi / 4. + self._phic / 2.), self._coef_b)

    def _compute_n(self) -> float:
        return sin(self._phip)

    def _compute_r0(self) -> float:
        return self._kp * self._coef_a / tan(self._phip)

    def _compute_lambda(self, i_t: float, i_d: float, i_u: float) -> float:
        return self._lambda0 - self._compute_inv_v(i_t, i_d, i_u) / self._coef_b

    def _compute_phi(self, i_u: float) -> float:
        phi = i_u

        while True:
            tmp = self.___phi(i_u, phi)
            if abs(tmp - phi) > Epsg9819a._PRECISION:
                phi = tmp
            else:
                return tmp

    def ___phi(self, i_u: float, phi: float) -> float:
        esinphi = self._e * sin(phi)
        return 2 * (atan(pow(tan(i_u / 2. + pi / 4.) / self._t0, 1. / self._coef_b)
                * pow((1. + esinphi) / (1. - esinphi), self._e / 2.)) - pi / 4.)

    def _compute_inv_xp(self, southing: float) -> float:
        return southing - self._fn

    def _compute_inv_yp(self, westing: float) -> float:
        return westing - self._fe

    def _compute_inv_r(self, i_xp: float, i_yp: float) -> float:
        return sqrt(i_xp ** 2 + i_yp ** 2)

    def _compute_inv_theta(self, i_xp: float, i_yp: float) -> float:
        return atan2(i_yp, i_xp)

    def _compute_inv_d(self, i_xp: float, i_yp: float) -> float:
        return self._compute_inv_theta(i_xp, i_yp) / sin(self._phip)

    def _compute_inv_t(self, i_xp: float, i_yp: float) -> float:
        return 2. * (atan(pow(self._r0 / self._compute_inv_r(i_xp, i_yp),
                              1. / self._n) * tan(pi / 4. + self._phip / 2.)) - pi / 4.)

    def _compute_inv_u(self, i_t: float, i_d: float) -> float:
        return asin(cos(self._alphac) * sin(i_t) - sin(self._alphac) * cos(i_t) *  cos(i_d))

    def _compute_inv_v(self, i_t: float, i_d: float, i_u: float) -> float:
        return asin(cos(i_t) * sin(i_d) / cos(i_u))


class Epsg9819b(Epsg9819a):
    """EPSG:9819

    Krovak
    """

    @override
    def _compute_d(self, u: float, v: float, t: float) -> float:
        return Epsg9819b.compute_d(u, v, t, self._alphac)

    @staticmethod
    def compute_d(u: float, v: float, t: float, alphac: float):
        """Calcul du coefficient D pour des longitudes excédant l'intervalle -90;+90."""
        return atan2(cos(u) * sin(v) / cos(t), (cos(alphac) * sin(t) - sin(u)) / sin(alphac) / cos(t))


class Epsg1041a(Epsg9819a):
    """EPSG:1041

    Krovak (North Orientated)
    """

    @override
    def compute(self, i):
        output = super().compute(i)
        return -output[Epsg9819a._NORTHING], -output[Epsg9819a._EASTING]

    @override
    def inverse(self, i):
        return super().inverse([-i[Epsg9819a._NORTHING], -i[Epsg9819a._EASTING]])


class Epsg1041b(Epsg1041a):
    """EPSG:1041

    Krovak (North Orientated)
    """
    @override
    def _compute_d(self, u: float, v: float, t: float) -> float:
        return Epsg9819b.compute_d(u, v, t, self._alphac)


class Epsg1042a(Epsg9819a):
    """EPSG::1042

    Krovak Modified
    """

    _SOUTHING = 0
    _WESTING = 1

    def __init__(self, ellipsoid: Ellipsoid,
                 phic: float, lambda0: float, alphac: float, phip: float, kp: float, ef: float, nf: float,
                 x0: float, y0: float,
                 c1: float, c2: float, c3: float, c4: float, c5: float,
                 c6: float, c7: float, c8: float, c9: float, c10: float):
        super().__init__(ellipsoid, phic, lambda0, alphac, phip, kp, ef, nf)
        self._x0 = x0
        self._y0 = y0
        self._c1 = c1
        self._c2 = c2
        self._c3 = c3
        self._c4 = c4
        self._c5 = c5
        self._c6 = c6
        self._c7 = c7
        self._c8 = c8
        self._c9 = c9
        self._c10 = c10

    @override
    def compute(self, i):
        u = self._compute_u(i[Epsg9819a._PHI])
        v = self._compute_v(i[Epsg9819a._LAMBDA])
        t = self._compute_t(u, v)
        r = self._r(u, v, t)
        theta = self._theta(u, v, t)
        xp = r * cos(theta)
        yp = r * sin(theta)
        xr = xp - self._x0
        yr = yp - self._y0
        return xp - self._dx(xr, yr) + self._fn, yp - self._dy(xr, yr) + self._fe

    @override
    def inverse(self, i):
        i_xp = self._inv_xp(i)
        i_yp = self._inv_yp(i)
        i_t = self._compute_inv_t(i_xp, i_yp)
        i_d = self._compute_inv_d(i_xp, i_yp)
        i_u = self._compute_inv_u(i_t, i_d)
        return self._compute_phi(i_u), self._compute_lambda(i_t, i_d, i_u)

    def _dx(self, x: float, y: float) -> float:
        x2 = x ** 2
        y2 = y ** 2

        return (self._c1
                + self._c3 * x
                - self._c4 * y
                - 2. * self._c6 * x * y
                + self._c5 * (x2 - y2)
                + self._c7 * x * (x2 - 3. * y2)
                - self._c8 * y * (3. * x2 - y2)
                + 4. * self._c9 * x * y * (x2 - y2)
                + self._c10 * (x2 * x2 + y2 * y2 - 6. * x2 * y2))

    def _dy(self, x: float, y: float) -> float:
        x2 = x ** 2
        y2 = y ** 2
        return (self._c2
                + self._c3 * y
                + self._c4 * x
                + 2. * self._c5 * x * y
                + self._c6 * (x2 - y2)
                + self._c8 * x * (x2 - 3. * y2)
                + self._c7 * y * (3. * x2 - y2)
                - 4. * self._c10 * x * y * (x2 - y2)
                + self._c9 * (x2 * x2 + y2 * y2 - 6. * x2 * y2))

    def _inv_xp(self, i) -> float:
        xrp = i[Epsg1042a._SOUTHING] - self._fn - self._x0
        yrp = i[Epsg1042a._WESTING] - self._fe - self._y0
        return i[Epsg1042a._SOUTHING] - self._fn + self._dx(xrp, yrp)

    def _inv_yp(self, i) -> float:
        xrp = i[Epsg1042a._SOUTHING] - self._fn - self._x0
        yrp = i[Epsg1042a._WESTING] - self._fe - self._y0
        return i[Epsg1042a._WESTING] - self._fe + self._dy(xrp, yrp)


class Epsg1042b(Epsg1042a):
    """EPSG::1042

    Krovak Modified
    """

    @override
    def _compute_d(self, u: float, v: float, t: float) -> float:
        return Epsg9819b.compute_d(u, v, t, self._alphac)


class Epsg1043a(Epsg1042a):
    """EPSG:1043

    Krovak Modified (North Orientated)
    """

    @override
    def compute(self, i):
        output = super().compute(i)
        return -output[Epsg1042a._WESTING], -output[Epsg1042a._SOUTHING]

    @override
    def inverse(self, i):
        return super().inverse([-i[Epsg1042a._WESTING], -i[Epsg1042a._SOUTHING]])


class Epsg1043b(Epsg1043a):
    """EPSG:1043

    Krovak Modified (North Orientated)
    """
    @override
    def _compute_d(self, u: float, v: float, t: float) -> float:
        return Epsg9819b.compute_d(u, v, t, self._alphac)


class Epsg1044(InvertibleProjection[Ellipsoid]):
    """Mercator variant C"""

    _PHI = 0
    _LAMBDA = 1
    _EASTING = 0
    _NORTHING = 1

    def __init__(self, ellipsoid: Ellipsoid, phi1: float, lambda0: float, phif: float, ef: float, nf: float):
        self._ellipsoid = ellipsoid
        self._a = ellipsoid.a()
        self._e = ellipsoid.e()
        self._phi1 = abs(phi1)
        self._lambda0 = lambda0
        self._phif = phif
        self._ef = ef
        self._nf = nf
        self._e2 = self._e ** 2
        self._k0 = self._compute_k0()
        self._m = self._a * self._k0 * log(tan(pi / 4. + phif / 2.) * self._esinphi(phif))

    @override
    def get_surface(self) -> Ellipsoid:
        return self._ellipsoid

    def _compute_k0(self):
        return cos(self._phi1) / sqrt((1. - self._e2 * sin(self._phi1) * sin(self._phi1)))

    def _esinphi(self, phi: float) -> float:
        sinphi = sin(phi)
        return pow((1. - self._e * sinphi) / (1. + self._e * sinphi), self._e / 2.)

    @override
    def compute(self, i):
        phi = i[Epsg1044._PHI]
        return self._ef + self._a * self._k0 * (i[Epsg1044._LAMBDA] - self._lambda0), \
            self._nf - self._m + self._a * self._k0 * log(tan(pi / 4. + phi / 2.) * self._esinphi(phi))

    @override
    def inverse(self, i):
        return self.__phi(i[Epsg1044._NORTHING]), \
            (i[Epsg1044._EASTING] - self._ef) / (self._a * self._k0) + self._lambda0

    def __phi(self, northing: float) -> float:
        t = exp((self._nf - self._m - northing) / (self._a * self._k0))
        chi = pi / 2. - 2. * atan(t)
        e2 = self._e2
        return chi + e2 * ((.5 + e2 * (5. / 24. + e2 * (1. / 12. + 13. * e2 / 360.))) * sin(2. * chi)
                           + e2 * ((7. / 48. + e2 * (29. / 240. + e2 * 811. / 11520.)) * sin(4. * chi)
                                   + e2 * ((7. / 120. + e2 * 81. / 1120.) * sin(6. * chi)
                                           + e2 * 4279. / 161280. * sin(8. * chi))))


class Epsg1051(InvertibleProjection[Ellipsoid]):
    """Lambert Conic Conformal (2SP Michigan)"""

    _PHI = 0
    _LAMBDA = 1
    _EASTING = 0
    _NORTHING = 1

    _PRECISION = 1e-12

    def __init__(self,
                 ellipsoid: Ellipsoid,
                 phif: float,
                 lambdaf: float,
                 phi1: float,
                 phi2: float,
                 ef: float,
                 nf: float,
                 k: float):
        self._ellipsoid = ellipsoid
        self._a = ellipsoid.a()
        self._e = ellipsoid.e()
        self._phif = phif
        self._lambdaf = lambdaf
        self._phi1 = phi1
        self._phi2 = phi2
        self._ef = ef
        self._nf = nf
        self._k = k
        self._m1 = self._compute_m(phi1)
        self._m2 = self._compute_m(phi2)
        self._t1 = self._compute_t(phi1)
        self._t2 = self._compute_t(phi2)
        self._n = self._compute_n()
        self._f = self._compute_f()
        self._rf = self._compute_r(phif)

    @override
    def get_surface(self) -> Ellipsoid:
        return self._ellipsoid

    @override
    def compute(self, i):
        p = i[Epsg1051._PHI]
        l = i[Epsg1051._LAMBDA]
        return self._compute_easting(p, l), self._compute_northing(p, l)

    @override
    def inverse(self, i):
        easting = i[Epsg1051._EASTING]
        northing = i[Epsg1051._NORTHING]
        return self._compute_phi(easting, northing), self._compute_lambda(easting, northing)

    def _compute_easting(self, p: float, l: float) -> float:
        return self._ef + self._compute_r(p) * sin(self._theta(l))

    def _compute_northing(self, p: float, l: float) -> float:
        return self._nf + self._rf - self._compute_r(p) * cos(self._theta(l))

    def _compute_m(self, p: float) -> float:
        sinphi = sin(p)
        return cos(p) / sqrt(1. - self._e * self._e * sinphi * sinphi)

    def _compute_t(self, p: float) -> float:
        esinphi = self._e * sin(p)
        return tan(pi / 4. - p / 2.) / pow((1. - esinphi) / (1. + esinphi), self._e / 2.)

    def _compute_n(self) -> float:
        return (log(self._m1) - log(self._m2)) / (log(self._t1) - log(self._t2))

    def _compute_f(self) -> float:
        return self._m1 / (self._n * pow(self._t1, self._n))

    def _compute_r(self, p: float) -> float:
        t = self._compute_t(p)
        return self._a * self._k * self._f * pow(t, self._n) if t > 0. else 0.

    def _theta(self, l: float) -> float:
        return self._n * (l - self._lambdaf)

    def _compute_lambda(self, easting: float, northing: float) -> float:
        return self._inv_theta(easting, northing) / self._n + self._lambdaf

    def _compute_phi(self, easting: float, northing: float) -> float:
        phi = self._inv_t(easting, northing)

        while True:
            tmp = self.___phi(easting, northing, phi)
            if abs(tmp - phi) > Epsg1051._PRECISION:
                phi = tmp
            else:
                return tmp

    def ___phi(self, easting: float, northing: float, phi: float) -> float:
        return (pi / 2.
                - 2. * atan(self._inv_t(easting, northing)
                            * pow((1. - self._e * sin(phi)) / (1 + self._e * sin(phi)), self._e / 2.)))

    def _inv_theta(self, easting: float, northing: float) -> float:
        return atan2(easting - self._ef, self._rf - (northing - self._nf))

    def _inv_t(self, easting: float, northing: float) -> float:
        return pow(self._inv_r(easting, northing) / (self._a * self._k * self._f), 1. / self._n)

    def _inv_r(self, easting: float, northing: float) -> float:
        rel_easting = easting - self._ef
        rel_northing = self._rf - (northing - self._nf)
        result = sqrt(rel_easting * rel_easting + rel_northing * rel_northing)
        return result if self._n > 0. else -result


class Epsg1052(InvertibleProjection[Ellipsoid]):
    """Colombia Urban"""

    _PHI = 0
    _LAMBDA = 1
    _EASTING = 0
    _NORTHING = 1

    def __init__(self, ellipsoid: Ellipsoid, phi0: float, lambda0: float, h0: float, fe: float, fn: float):
        self._ellipsoid = ellipsoid
        self._e2 = ellipsoid.e2()
        self._h0 = h0
        self._fe = fe
        self._fn = fn
        self._phi0 = phi0
        self._lambda0 = lambda0
        self._nu0 = ellipsoid.nu(phi0)
        self._coef_a = 1. + h0 / self._nu0
        self._rho0 = ellipsoid.rho(phi0)
        self._coef_b = tan(phi0) / (2. * self._rho0 * self._nu0)
        self._coef_c = 1. + h0 / ellipsoid.a()
        self._coef_d = self._rho0 * (1. + h0 / (ellipsoid.a() * (1. - self._e2)))

    def compute(self, i):
        phi = i[Epsg1052._PHI]
        l = i[Epsg1052._LAMBDA] - self._lambda0
        phim = (self._phi0 + phi) / 2.
        rhom = self._ellipsoid.rho(phim)
        nu = self._ellipsoid.nu(phi)
        coef_g = 1 + self._h0 / rhom
        cosphi = cos(phi)
        return self._fe + self._coef_a * nu * cosphi * l, \
            self._fn + coef_g * self._rho0 * ((phi - self._phi0) + (self._coef_b * l * l * nu * nu * cosphi * cosphi))

    @override
    def get_surface(self) -> Ellipsoid:
        return self._ellipsoid

    @override
    def inverse(self, i):
        de = (i[Epsg1052._EASTING] - self._fe) / self._coef_c
        phi = self._phi0 + (i[Epsg1052._NORTHING] - self._fn) / self._coef_d - self._coef_b * de * de
        return phi, self._lambda0 + de / (self._ellipsoid.nu(phi) * cos(phi))


class Epsg9801(InvertibleProjection[Ellipsoid]):
    """Lambert Conic Conformal (1SP)"""

    _PHI = 0
    _LAMBDA = 1
    _EASTING = 0
    _NORTHING = 1
    _PRECISION = 1e-12

    def __init__(self, ellipsoid: Ellipsoid, phi0: float, lambda0: float, k0: float, fe: float, fn: float):
        self._ellipsoid = ellipsoid
        self._a = ellipsoid.a()
        self._e = ellipsoid.e()
        self._phi0 = phi0
        self._lambda0 = lambda0
        self._k0 = k0
        self._fe = fe
        self._fn = fn
        self._n = self._compute_n()
        self._f = self._compute_f()
        self._r0 = self._compute_r(phi0)

    @override
    def get_surface(self) -> Ellipsoid:
        return self._ellipsoid

    @override
    def compute(self, i):
        phi = i[Epsg9801._PHI]
        l = i[Epsg9801._LAMBDA]
        return self._compute_easting(phi, l), self._compute_northing(phi, l)

    @override
    def inverse(self, i):
        easting = i[Epsg9801._EASTING]
        northing = i[Epsg9801._NORTHING]
        return self._compute_phi(easting, northing), self._compute_lambda(easting, northing)

    def _compute_easting(self, phi: float, l: float):
        return self._fe + self._compute_r(phi) * sin(self._compute_theta(l))

    def _compute_northing(self, phi: float, l: float):
        return self._fn + self._r0 - self._compute_r(phi) * cos(self._compute_theta(l))

    def _compute_m(self, phi: float):
        sinphi = sin(phi)
        return cos(phi) / sqrt(1. - self._e * self._e * sinphi * sinphi)

    def _compute_t(self, phi: float):
        esinphi = self._e * sin(phi)
        return tan(pi / 4. - phi / 2.) / pow((1. - esinphi) / (1. + esinphi), self._e / 2.)

    def _compute_n(self):
        return sin(self._phi0)

    def _compute_f(self):
        return self._compute_m(self._phi0) / (self._n * pow(self._compute_t(self._phi0), self._n))

    def _compute_r(self, phi: float):
        t = self._compute_t(phi)
        return self._a * self._f * pow(t, self._n) * self._k0 if t > 0. else 0.

    def _compute_theta(self, l: float):
        return self._n * (l - self._lambda0)

    def _compute_lambda(self, easting: float, northing: float):
        return self._compute_inv_theta(easting, northing) / self._n + self._lambda0

    def _compute_phi(self, easting: float, northing: float):
        phi = self._compute_inv_t(easting, northing)

        while True:
            tmp = self.__compute_phi(easting, northing, phi)
            if abs(tmp - phi) > Epsg9801._PRECISION:
                phi = tmp
            else:
                return tmp

    def __compute_phi(self, easting: float, northing: float, phi: float):
        return pi / 2. - 2. * atan(
                self._compute_inv_t(easting, northing) * pow((1. - self._e * sin(phi)) / (1 + self._e * sin(phi)),
                                                             self._e / 2.))

    def _compute_inv_theta(self, easting: float, northing: float):
        return atan2(easting - self._fe, self._r0 - (northing - self._fn))

    def _compute_inv_t(self, easting: float, northing: float):
        return pow(self._compute_inv_r(easting, northing) / (self._a * self._f), 1. / self._n)

    def _compute_inv_r(self, easting: float, northing: float):
        rel_easting = easting - self._fe
        rel_northing = self._r0 - (northing - self._fn)
        result = sqrt(rel_easting ** 2 + rel_northing ** 2)
        return result if self._n > 0. else -result
