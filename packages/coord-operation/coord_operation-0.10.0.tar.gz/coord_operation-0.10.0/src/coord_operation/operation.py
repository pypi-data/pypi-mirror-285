"""The operation hierachy model."""
from typing import override

from coord_operation.surface import Surface


class Operation:
    """
    EPSG definition:

    "Process using a mathematical model, based on a one-to-one relationship, that changes coordinates in a source
    coordinate reference system to coordinates in a target coordinate reference system, or that changes coordinates at a
    source coordinate epoch to coordinates at a target coordinate epoch within the same coordinate reference system."
    """

    def compute(self, i):
        """Compute the operation over an input (ordinarily coordinates).

        Args:
            i: the input

        Returns: the operation result (ordinarily output coordinates)

        """

    def __call__(self, *args, **kwargs):
        return self.compute(*args)


class InvertibleOperation(Operation):
    """An invertible operation is an operation able to recompute the inputs of the compute method given its output as
    a parameter to the inverse method."""

    def inverse(self, i):
        """The inverse operation that allows to produce the compute method input from its output."""

    def inverse_operation(self) -> Operation:
        """The operation for which the compute method is defined by the inverse method of the current invertible
        operation instance.
        """

    def __invert__(self) -> Operation:
        return self.inverse_operation()


class Conversion[S: Surface](Operation):
    """EPSG definition:

    A coordinate operation that changes coordinates in a source coordinate reference system to coordinates in a target
    coordinate reference system in which both coordinate reference systems are based on the same datum.
    """

    def get_surface(self) -> S:
        """
        Returns (Surface): the reference surface
        """


class AutoInverse(InvertibleOperation):
    """An auto-inverse operation is a proxy-utilitary class that allows to automatically define the inverse operation
    from the current invertible operation."""

    @override
    def inverse_operation(self) -> InvertibleOperation:
        return _AnonymAutoInverse(direct=self)


class _AnonymAutoInverse(AutoInverse):

    def __init__(self, direct: AutoInverse):
        self._direct = direct

    @override
    def inverse(self, i):
        return self._direct.compute(i)

    @override
    def compute(self, i):
        return self._direct.inverse(i)

    @override
    def inverse_operation(self) -> InvertibleOperation:
        return self._direct


class Projection[S: Surface](Conversion[S]):
    """EPSG definition:
    Coordinate conversion from an ellipsoidal coordinate system to a plane."""


class InvertibleProjection[S: Surface](Projection[S], AutoInverse):
    """A projection which can be inverted to compute the ellipsoidal coordinate system coordinates from the projected
    ones."""
