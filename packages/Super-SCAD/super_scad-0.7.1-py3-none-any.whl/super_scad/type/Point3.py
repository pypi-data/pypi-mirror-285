import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point3:
    """
    A point in 3D space.
    """
    x: float
    """
    The x-coordinate of this point.
    """

    y: float
    """
    The y-coordinate of this point.
    """

    z: float
    """
    The z-coordinate of this point.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return f"[{self.x}, {self.y}, {self.z}]"

    # ------------------------------------------------------------------------------------------------------------------
    def __add__(self, other):
        return Point3(self.x + other.x, self.y + other.y, self.z + other.z)

    # ------------------------------------------------------------------------------------------------------------------
    def __sub__(self, other):
        return Point3(self.x - other.x, self.y - other.y, self.z - other.z)

    # ------------------------------------------------------------------------------------------------------------------
    def __truediv__(self, other: float):
        return Point3(self.x / other, self.y / other, self.z / other)

    # ------------------------------------------------------------------------------------------------------------------
    def __mul__(self, other: float):
        return Point3(self.x * other, self.y * other, self.z * other)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def length(self) -> float:
        """
        Returns the length of this vector.
        """
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def normal(self):
        """
        Returns the unit vector of this vector.

        :rtype: super_scad.type.Point3.Point3
        """
        length = self.length

        return Point3(self.x / length, self.y / length, self.z / length)

# ----------------------------------------------------------------------------------------------------------------------
