from super_scad.d3.private.PrivateCube import PrivateCube
from super_scad.scad.ArgumentAdmission import ArgumentAdmission
from super_scad.scad.Context import Context
from super_scad.scad.ScadWidget import ScadWidget


class Cube(ScadWidget):
    """
    Widget for creating cubes. See https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Primitive_Solids#cube.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 size: float,
                 center: bool = False):
        """
        Object constructor.

        :param size: The size of the cube.
        :param center: Whether the cube is centered at the origin.
        """
        ScadWidget.__init__(self, args=locals())

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        admission = ArgumentAdmission(self._args)
        admission.validate_required({'size'}, {'center'})

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def center(self) -> bool:
        """
        Returns whether the cube is centered at the origin.
        """
        return self._args['center']

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def size(self) -> float:
        """
        Returns the size of the cube.
        """
        return self.uc(self._args['size'])

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        return PrivateCube(size=self.size, center=self.center)

# ----------------------------------------------------------------------------------------------------------------------
