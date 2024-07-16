import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point2:
    """
    A point in 2D space or a 2-dimensional vector.
    """
    # ------------------------------------------------------------------------------------------------------------------
    x: float
    """
    The x-coordinate of this point.
    """

    y: float
    """
    The y-coordinate of this point.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return f"[{self.x}, {self.y}]"

    # ------------------------------------------------------------------------------------------------------------------
    def __add__(self, other):
        return Point2(self.x + other.x, self.y + other.y)

    # ------------------------------------------------------------------------------------------------------------------
    def __sub__(self, other):
        return Point2(self.x - other.x, self.y - other.y)

    # ------------------------------------------------------------------------------------------------------------------
    def __truediv__(self, other: float):
        return Point2(self.x / other, self.y / other)

    # ------------------------------------------------------------------------------------------------------------------
    def __mul__(self, other: float):
        return Point2(self.x * other, self.y * other)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def from_polar_coordinates(length: float, angle: float):
        """
        Creates a 2-dimensional vector from polar coordinates.

        @param length: The length of the vector.
        @param angle: The angle of the vector.
        """
        return Point2(length * math.cos(math.radians(angle)), length * math.sin(math.radians(angle)))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def length(self) -> float:
        """
        Returns the length of this vector.
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def normal(self):
        """
        Returns the unit vector of this vector.

        :rtype: super_scad.type.Point2.Point2
        """
        length = self.length

        return Point2(self.x / length, self.y / length)

# ----------------------------------------------------------------------------------------------------------------------
