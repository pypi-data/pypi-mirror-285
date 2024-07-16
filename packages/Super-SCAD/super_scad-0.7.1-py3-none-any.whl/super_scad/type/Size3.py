from dataclasses import dataclass


@dataclass(frozen=True)
class Size3:
    """
    Size in a 3D space.
    """
    width: float
    """
    The width.
    """

    depth: float
    """
    The depth.
    """

    height: float
    """
    The height.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return f"[{self.width}, {self.depth}, {self.height}]"

# ----------------------------------------------------------------------------------------------------------------------
