from typing import Dict

from super_scad.private.PrivateSingleChildOpenScadCommand import PrivateSingleChildOpenScadCommand
from super_scad.scad.ArgumentAdmission import ArgumentAdmission
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.type.Color import Color


class Paint(PrivateSingleChildOpenScadCommand):
    """
    Paints a child widget using a specified color and opacity. See
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#color.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 color: Color,
                 child: ScadWidget) -> None:
        """
        Object constructor.

        :param color: The color and opacity of the child widget.
        :param child: The child widget to be painted.
        """
        PrivateSingleChildOpenScadCommand.__init__(self, command='color', args=locals(), child=child)

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        admission = ArgumentAdmission(self._args)
        admission.validate_exclusive({'color'})

    # ------------------------------------------------------------------------------------------------------------------
    def argument_map(self) -> Dict[str, str]:
        """
        Returns the map from SuperSCAD arguments to OpenSCAD arguments.
        """
        return {'color': 'c'}

# ----------------------------------------------------------------------------------------------------------------------
