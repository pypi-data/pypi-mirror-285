from super_scad.boolean.Intersection import Intersection
from super_scad.d2.Circle import Circle
from super_scad.d2.Rectangle import Rectangle
from super_scad.d3.LinearExtrude import LinearExtrude
from super_scad.scad.ArgumentAdmission import ArgumentAdmission
from super_scad.scad.Context import Context
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.transformation.Translate2D import Translate2D


class Semicircle(ScadWidget):
    """
    Widget for creating semicircles.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 height: float | None = None,
                 radius: float | None = None,
                 diameter: float | None = None,
                 fa: float | None = None,
                 fs: float | None = None,
                 fn: int | None = None,
                 fn4n: bool | None = None):
        """
        Object constructor.

        :param height: The height of the pie slice. If height is None, a 2D widget will be created.
        :param radius: The radius of the semicircles.
        :param diameter: The diameter of the semicircles.
        :param fa: The minimum angle (in degrees) of each fragment.
        :param fs: The minimum circumferential length of each fragment.
        :param fn: The fixed number of fragments in 360 degrees. Values of 3 or more override fa and fs.
        :param fn4n: Whether to create a semicircles based on circle with a multiple of 4 vertices.
        """
        ScadWidget.__init__(self, args=locals())

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        admission = ArgumentAdmission(self._args)
        admission.validate_exclusive({'radius'}, {'diameter'})
        admission.validate_exclusive({'fn4n'}, {'fa', 'fs', 'fn'})
        admission.validate_required({'radius', 'diameter'})

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def height(self) -> float | None:
        """
        Returns teh height of the pie slice. If height is None, a 2D widget will be created.
        """
        return self.uc(self._args.get('height'))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def radius(self) -> float:
        """
        Returns the radius of the circle.
        """
        return self.uc(self._args.get('radius', 0.5 * self._args.get('diameter', 0.0)))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def diameter(self) -> float:
        """
        Returns the diameter of the circle.
        """
        return self.uc(self._args.get('diameter', 2.0 * self._args.get('radius', 0.0)))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fa(self) -> float | None:
        """
        Returns the minimum angle (in degrees) of each fragment.
        """
        return self._args.get('fa')

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fs(self) -> float | None:
        """
        Returns the minimum circumferential length of each fragment.
        """
        return self.uc(self._args.get('fs'))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fn(self) -> int | None:
        """
        Returns the fixed number of fragments in 360 degrees. Values of 3 or more override $fa and $fs.
        """
        return self._args.get('fn')

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fn4n(self) -> bool | None:
        """
        Returns whether to create a circle with multiple of 4 vertices.
        """
        return self._args.get('fn4n')

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        semicircle = Intersection(children=[Circle(diameter=self.diameter,
                                                   fa=self.fa,
                                                   fs=self.fs,
                                                   fn=self.fn,
                                                   fn4n=self.fn4n),
                                            Translate2D(x=-(self.radius + context.eps),
                                                        child=Rectangle(width=self.diameter + 2 * context.eps,
                                                                        depth=self.radius + context.eps))])
        if self.height is None:
            return semicircle

        return LinearExtrude(height=self.height, child=semicircle)

# ----------------------------------------------------------------------------------------------------------------------
