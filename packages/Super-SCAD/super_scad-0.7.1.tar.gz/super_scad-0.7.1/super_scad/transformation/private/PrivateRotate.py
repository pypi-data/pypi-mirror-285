from typing import Dict

from super_scad.private.PrivateSingleChildOpenScadCommand import PrivateSingleChildOpenScadCommand
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.type.Point2 import Point2
from super_scad.type.Point3 import Point3


class PrivateRotate(PrivateSingleChildOpenScadCommand):
    """
    Rotates its child widget about the axis of the coordinate system or around an arbitrary axis. See
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#rotate.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 angle: float | Point2 | Point3,
                 vector: Point3 | None = None,
                 child: ScadWidget) -> None:
        """
        Object constructor.

        :param angle: The angle of the rotation.
        :param vector: The vector of the rotation.
        :param child: The widget to be rotated.
        """
        PrivateSingleChildOpenScadCommand.__init__(self, command='rotate', args=locals(), child=child)

    # ------------------------------------------------------------------------------------------------------------------
    def argument_map(self) -> Dict[str, str]:
        """
        Returns the map from SuperSCAD arguments to OpenSCAD arguments.
        """
        return {'angle': 'a', 'vector': 'v'}

# ----------------------------------------------------------------------------------------------------------------------
