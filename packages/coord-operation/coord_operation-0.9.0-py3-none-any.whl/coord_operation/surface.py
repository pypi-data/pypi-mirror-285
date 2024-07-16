"""
The module define the surface types in usage in geomatics and geodesy.
"""


from enum import Enum, auto
from typing import override

from math import sqrt, log, floor, pi, sin, asin, cos


class Surface:
    """An abstract type of surfaces."""

    def semi_major_axis(self) -> float:
        """An abstract method to return the semi-major axis value for all surface kinds."""


class Parameter(Enum):
    """An enum to specify the way an ellipsoid is defined. It refers to the semantics of the second parameter given
    along with the semi-major axis.
    """
    SEMI_MINOR_AXIS = auto()
    INVERSE_FLATTENING = auto()
    FLATTENING = auto()
    ECCENTRICITY = auto()


class Ellipsoid(Surface):
    """An ellipsoidal surface defined by two axis lengths. The first one is given by the semi-major axis parameter. The
    second one can be either directly defined using a semi-minor axis parameter or indirectly defined by the mean of
    eccentricity, inverse flattening or flattening which allow to compute the semi-minor axis value from the semi-major
    one."""

    def __init__(self, a: float, second_parameter: float, p: Parameter):
        self._a = a
        match p:
            case Parameter.SEMI_MINOR_AXIS:
                self._b = second_parameter
                self._inverse_flattening = a / (a - self._b)
                self._f = 1. / self._inverse_flattening
                self._e = sqrt(self._f * (2. - self._f))
            case Parameter.INVERSE_FLATTENING:
                self._inverse_flattening = second_parameter
                self._f = 1. / self._inverse_flattening
                self._b = a * (1. - self._f)
                self._e = sqrt(self._f * (2. - self._f))
            case Parameter.FLATTENING:
                self._f = second_parameter
                self._inverse_flattening = 1. / self._f
                self._b = a * (1. - self._f)
                self._e = sqrt(self._f * (2. - self._f))
            case Parameter.ECCENTRICITY:
                self._e = second_parameter
                self._b = a * sqrt(1. - self._e * self._e)
                self._inverse_flattening = a / (a - self._b)
                self._f = 1. / self._inverse_flattening
            case _:
                raise AttributeError()

        self._e2 = self._e ** 2
        self._second_eccentricity = sqrt(self._e2 / (1. - self._e2))
        self._e1 =  (1. - sqrt(1. - self._e2)) / (1. + sqrt(1. - self._e2))
        self._e12 = self._e1 ** 2
        self._ra = a * sqrt((1. - (1. - self._e2) / (2. * self._e)) * log((1. - self._e) / (1. + self._e)))
        self._mp = self.m(pi / 2.)
        self._mod = a - floor(a / self._b) * self._b
        self._qp = self.q(pi / 2.)
        self._rq = a * sqrt(self._qp / 2.)

    def a(self) -> float:
        """The semi-major axis value."""
        return self._a

    @override
    def semi_major_axis(self) -> float:
        return self.a()

    def b(self) -> float:
        """The semi-minor axis value."""
        return self._b

    def inverse_flattening(self) -> float:
        """inverse flattening"""
        return self._inverse_flattening

    def f(self) -> float:
        """flattening"""
        return self._f

    def e(self) -> float:
        """eccentricity"""
        return self._e

    def e2(self) -> float:
        """square eccentricity"""
        return self._e2

    def second_e(self) -> float:
        """second eccentricity"""
        return self._second_eccentricity

    def mod(self) -> float:
        """Map Projections"""
        return self._mod

    def rho(self, phi: float) -> float:
        """meridian curvature radius"""
        esinphi2: float = self.e_sin(phi)
        return self._a * (1. - self._e2) / (esinphi2 * sqrt(esinphi2))

    def e_sin(self, phi: float) -> float:
        """utility computation method"""
        return 1. - self._e2 * sin(phi) ** 2

    def e_sin_sqrt(self, phi: float) -> float:
        """utility computation method"""
        return sqrt(self.e_sin(phi))

    def nu(self, phi: float) -> float:
        """prime vertical curvature radius"""
        return self._a / self.e_sin_sqrt(phi)

    def ra(self) -> float:
        """authalic sphere radius"""
        return self._ra

    def qp(self) -> float:
        """Map Projections"""
        return self._qp

    def rq(self) -> float:
        """Map Projections"""
        return self._rq

    def beta_phi(self, phi: float) -> float:
        """Map Projections, formula 3-11"""
        return self.beta_q(self.q(phi))

    def beta_q(self, q: float) -> float:
        """Map Projections, formula 3-11"""
        return asin(q / self._qp)

    def q(self, phi: float) -> float:
        """Map Projections, formula 3-12"""
        sinphi: float = sin(phi)
        return (1. - self._e2) \
                * (sinphi / (1. - self._e2 * sinphi * sinphi)
                - (1. / (2. * self._e)) * log((1. - self._e * sinphi) / (1. + self._e * sinphi)))

    def phi(self, betap: float) -> float:
        """Map Projections, formula 3-18

        Approximate latitude from authalic latitude using a series.

        Args:
            betap (float): authalic latitude

        Returns (float): latitude
        """
        e2: float = self._e2
        return betap + e2 * ((1. / 3. + e2 * (31. / 180. + e2 * 517. / 5040.)) * sin(2. * betap)
                             + e2 * ((23. / 360. + e2 * 251. / 3780.) * sin(4. * betap)
                             + e2 * 761. / 45360. * sin(6. * betap)))

    def rc(self, phi: float) -> float:
        """conformal sphere radius"""
        return sqrt(1 - self._e2) * self.nu(phi)

    def rectifying_latitude(self, m: float) -> float:
        """Map Projections, formula 3-20

        rectifying latitude
        """
        return m / self.__mp() * (pi / 2.)

    def __mp(self) -> float:
        """Map Projections, formula 3-21

        Value of m(phi) / phi when phi = PI/2.
        """
        return self._mp

    def e1(self) -> float:
        """Map Projections, formula 3-24"""
        return self._e1

    def phi1(self, mu: float) -> float:
        """Map Projections, formula 3-26"""
        e1 = self._e1
        e12 = self._e12
        return mu + e1 * ((3. / 2. - e12 * 27. / 32.) * sin(2. * mu)
                + e1 * ((21. / 16. - e12 * 55. / 32.) * sin(4. * mu)
                + e1 * (151. / 96. * sin(6. * mu)
                + e1 * 1097. / 512. * sin(8. * mu))))

    def m(self, phi: float) -> float:
        """Map Projections, formula 3-21

        Distance along the meridian from the equator to latitude phi.
        """
        e2: float = self._e2
        return self._a * ((1. - e2 * (1. / 4. + e2 * (3. / 64. + e2 * 5. / 256.))) * phi
                + e2 * (-(3. / 8. + e2 * (3. / 32. + e2 * 45. / 1024.)) * sin(2. * phi)
                + e2 * ((15. / 256. + e2 * 45. / 1024.) * sin(4. * phi)
                + e2 * -35. / 3072. * sin(6. * phi))))

    def mu(self, m: float) -> float:
        """Map Projections, formula 7-19"""
        e2: float = self._e2
        return m / (self._a * (1. - e2 * (1. / 4. + e2 * (3. / 64. + e2 * (5. / 256.)))))

    def mp(self, phi: float) -> float:
        """Map Projections, formula 18-17"""
        e2: float = self._e2
        return (1. - e2 * (1. / 4. + e2 * (3. / 64. + e2 * 5. / 256.))) \
            + 2. * e2 * (-(3. / 8. + e2 * (3. / 32. + e2 * 45. / 1024.)) * cos(2. * phi)
                         + 4. * e2 * ((15. / 256. + e2 * 45. / 1024.) * cos(4. * phi)
                         + 6. * e2 * -35. / 3072. * cos(6. * phi)))

    @staticmethod
    def of_eccentricity(a: float, eccentricity: float):
        """Builds an ellipsoid from the semi-major axis and eccentricity values.
        Args:
            a (float): semi-major axis
            eccentricity (float): eccentricity

        Return (Ellipsoid)
        """
        return Ellipsoid(a=a, second_parameter=eccentricity, p=Parameter.ECCENTRICITY)

    @staticmethod
    def of_semi_minor_axis(a: float, b: float):
        """Builds an ellipsoid from the semi-major axis and semi-minor values.
        Args:
            a (float): semi-major axis
            b (float): semi-minor axis

        Return (Ellipsoid)
        """
        return Ellipsoid(a=a, second_parameter=b, p=Parameter.SEMI_MINOR_AXIS)

    @staticmethod
    def of_inverse_flattening(a: float, invf: float):
        """Builds an ellipsoid from the semi-major axis and inverse flattening values.
        Args:
            a (float): semi-major axis
            invf (float): inverse flattening

        Return (Ellipsoid)
        """
        return Ellipsoid(a=a, second_parameter=invf, p=Parameter.INVERSE_FLATTENING)

    @staticmethod
    def of_flattening(a: float, f: float):
        """Builds an ellipsoid from the semi-major axis and flattening values.
        Args:
            a (float): semi-major axis
            f (float): flattening

        Return (Ellipsoid)
        """
        return Ellipsoid(a=a, second_parameter=f, p=Parameter.FLATTENING)

    @staticmethod
    def of_square_eccentricity(a: float, e2: float):
        """Builds an ellipsoid from the semi-major axis and square eccentricity values.
        Args:
            a (float): semi-major axis
            e2 (float): square eccentricity

        Return (Ellipsoid)
        """
        return Ellipsoid(a=a, second_parameter=sqrt(e2), p=Parameter.ECCENTRICITY)


GRS_80 = Ellipsoid.of_inverse_flattening(a=6_378_137., invf=298.257)
"""Map Projections, table 1, page 12"""

WGS_72 = Ellipsoid.of_inverse_flattening(a=6_378_135., invf=298.26)
"""Map Projections, table 1, page 12"""

AUSTRALIAN = Ellipsoid.of_inverse_flattening(a=6_378_160., invf=298.25)
"""Map Projections, table 1, page 12"""

KRASOVSKY = Ellipsoid.of_inverse_flattening(a=6_378_245., invf=298.3)
"""Map Projections, table 1, page 12"""

INTERNATIONAL = Ellipsoid.of_inverse_flattening(a=6_378_388., invf=297.)
"""Map Projections, table 1, page 12"""

HAYFORD = Ellipsoid.of_inverse_flattening(a=6_378_388., invf=297.)
"""Map Projections, table 1, page 12"""

CLARKE_1880 = Ellipsoid.of_inverse_flattening(a=6_378_249.1, invf=293.46)
"""Map Projections, table 1, page 12"""

CLARKE_1866 = Ellipsoid.of_semi_minor_axis(a=6_378_206.4, b=6_356_583.8)
"""Map Projections, table 1, page 12"""

AIRY = Ellipsoid.of_semi_minor_axis(a=6_377_563.4, b=6_356_256.9)
"""Map Projections, table 1, page 12"""

BESSEL = Ellipsoid.of_semi_minor_axis(a=6_377_397.2, b=6_356_079.0)
"""Map Projections, table 1, page 12"""

EVEREST = Ellipsoid.of_semi_minor_axis(a=6_377_276.3, b=6_356_075.4)
"""Map Projections, table 1, page 12"""


class Spheroid(Surface):
    """A spheroid can be seen as a particular ellipsoid for which the semi-major axis and the semi-minor axis are equal.
    """

    def __init__(self, r: float):
        self._r = r

    def r(self) -> float:
        """
        Return (float): the sphere radius
        """
        return self._r

    @override
    def semi_major_axis(self) -> float:
        return self.r()

    @staticmethod
    def of_radius(r: float):
        """Build a spheroid for a given radius.
        Args:
            r (float): the sphere radius

        Return (Spheroid)
        """
        return Spheroid(r=r)

    @staticmethod
    def unit():
        """
        Return (Spheroid): the unit sphere instance
        """
        return _UNIT


_UNIT = Spheroid.of_radius(1)
