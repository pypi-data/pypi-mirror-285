from super_scad.scad.ArgumentAdmission import ArgumentAdmission
from super_scad.scad.Context import Context
from super_scad.scad.ScadSingleChildParent import ScadSingleChildParent
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.transformation.private.PrivateTranslate import PrivateTranslate
from super_scad.type.Point3 import Point3


class Translate3D(ScadSingleChildParent):
    """
    Translates (moves) its child widget along the specified vector. See
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#translate.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 vector: Point3 | None = None,
                 x: float | None = None,
                 y: float | None = None,
                 z: float | None = None,
                 child: ScadWidget):
        """
        Object constructor.

        :param vector: The vector over which the child widget is translated.
        :param x: The distance the child widget is translated along the x-axis.
        :param y: The distance the child widget is translated along the y-axis.
        :param z: The distance the child widget is translated along the z-axis.
        :param child: The child widget to be translated.
        """
        ScadSingleChildParent.__init__(self, args=locals(), child=child)

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        admission = ArgumentAdmission(self._args)
        admission.validate_exclusive({'vector'}, {'x', 'y', 'z'})

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def vector(self) -> Point3:
        """
        Returns the vector over which the child widget is translated.
        """
        return Point3(self.x, self.y, self.z)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def x(self) -> float:
        """
        Returns distance the child widget is translated to along the x-axis.
        """
        if 'vector' in self._args:
            return self.uc(self._args['vector'].x)

        return self.uc(self._args.get('x', 0.0))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def y(self) -> float:
        """
        Returns distance the child widget is translated to along the y-axis.
        """
        if 'vector' in self._args:
            return self.uc(self._args['vector'].y)

        return self.uc(self._args.get('y', 0.0))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def z(self) -> float:
        """
        Returns distance the child widget is translated to along the z-axis.
        """
        if 'vector' in self._args:
            return self.uc(self._args['vector'].z)

        return self.uc(self._args.get('z', 0.0))

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        return PrivateTranslate(vector=Point3(x=self.x, y=self.y, z=self.z), child=self.child)

# ----------------------------------------------------------------------------------------------------------------------
