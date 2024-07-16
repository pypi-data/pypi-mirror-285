from typing import Dict, Set

from super_scad.private.PrivateOpenScadCommand import PrivateOpenScadCommand
from super_scad.scad.ArgumentAdmission import ArgumentAdmission


class PrivateCylinder(PrivateOpenScadCommand):
    """
    Widget for creating cylinders and cones. See https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Primitive_Solids#cylinder.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 height: float,
                 radius: float | None = None,
                 diameter: float | None = None,
                 bottom_radius: float | None = None,
                 bottom_diameter: float | None = None,
                 top_radius: float | None = None,
                 top_diameter: float | None = None,
                 center: bool = False,
                 fa: float | None = None,
                 fs: float | None = None,
                 fn: int | None = None):
        """
        Object constructor.

        :param height: The height of the cone or cylinder.
        :param radius: The radius of the cylinder.
        :param diameter: The diameter of the cylinder.
        :param top_radius: The radius at the top of the cone.
        :param top_diameter: The diameter at the top of the cone.
        :param bottom_radius: The radius at the bottom of the cone.
        :param bottom_diameter: The diameter at the bottom of the cone.
        :param center: Whether the cone is centered in the z-direction.
        :param fa: The minimum angle (in degrees) of each fragment.
        :param fs: The minimum circumferential length of each fragment.
        :param fn: The fixed number of fragments in 360 degrees. Values of 3 or more override fa and fs.
        """
        PrivateOpenScadCommand.__init__(self, command='cylinder', args=locals())

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        admission = ArgumentAdmission(self._args)
        admission.validate_exclusive({'radius'}, {'diameter'})
        admission.validate_exclusive({'top_radius'}, {'top_diameter'}, {'radius'}, {'diameter'})
        admission.validate_exclusive({'bottom_radius'}, {'bottom_diameter'}, {'radius'}, {'diameter'})
        admission.validate_required({'height'},
                                    {'radius', 'diameter', 'bottom_radius', 'bottom_diameter'},
                                    {'radius', 'diameter', 'top_radius', 'top_diameter'},
                                    {'center'})

    # ------------------------------------------------------------------------------------------------------------------
    def argument_map(self) -> Dict[str, str]:
        """
        Returns the map from SuperSCAD arguments to OpenSCAD arguments.
        """
        return {'height':          'h',
                'radius':          'r',
                'diameter':        'd',
                'bottom_radius':   'r1',
                'bottom_diameter': 'd1',
                'top_radius':      'r2',
                'top_diameter':    'd2',
                'fa':              '$fa',
                'fs':              '$fs',
                'fn':              '$fn'}

    # ------------------------------------------------------------------------------------------------------------------
    def argument_lengths(self) -> Set[str]:
        """
        Returns the set with arguments that are lengths.
        """
        return {'h', 'r', 'r1', 'r2', 'd', 'd1', 'd2', '$fs'}

# ----------------------------------------------------------------------------------------------------------------------
