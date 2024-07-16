from super_scad.scad.Context import Context
from super_scad.scad.ScadSingleChildParent import ScadSingleChildParent
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.transformation.private.PrivateRotate import PrivateRotate
from super_scad.type.Angle import Angle


class Rotate2D(ScadSingleChildParent):
    """
    Rotates its child about the z-axis. See https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#rotate.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 angle: float | None = None,
                 child: ScadWidget) -> None:
        """
        Object constructor.

        :param angle: The angle of rotation (around the z-axis).
        :param child: The child widget to be rotated (around the z-axis).
        :param child: The widget to be rotated.
        """
        ScadSingleChildParent.__init__(self, args=locals(), child=child)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def angle(self) -> float:
        """
        Returns the angle of rotation (around the z-axis).
        """
        return Angle.normalize(self._args.get('angle', 0.0))

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        return PrivateRotate(angle=self.angle, child=self.child)

# ----------------------------------------------------------------------------------------------------------------------
