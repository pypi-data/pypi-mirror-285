from typing import Dict

from super_scad.private.PrivateSingleChildOpenScadCommand import PrivateSingleChildOpenScadCommand
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.type.Point2 import Point2
from super_scad.type.Point3 import Point3


class PrivateScale(PrivateSingleChildOpenScadCommand):
    """
    Scales its child widget using the specified vector. See
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#scale.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 factor: Point2 | Point3,
                 child: ScadWidget) -> None:
        """
        Object constructor.

        :param factor: The scaling factor to apply.
        :param child: The child widget to be scaled.
        """
        PrivateSingleChildOpenScadCommand.__init__(self, command='scale', args=locals(), child=child)

    # ------------------------------------------------------------------------------------------------------------------
    def argument_map(self) -> Dict[str, str]:
        """
        Returns the map from SuperSCAD arguments to OpenSCAD arguments.
        """
        return {'factor': 'v'}

# ----------------------------------------------------------------------------------------------------------------------
