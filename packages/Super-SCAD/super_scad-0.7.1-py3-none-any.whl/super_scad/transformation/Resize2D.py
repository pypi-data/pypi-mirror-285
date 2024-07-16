from typing import Tuple

from super_scad.scad.ArgumentAdmission import ArgumentAdmission
from super_scad.scad.Context import Context
from super_scad.scad.ScadSingleChildParent import ScadSingleChildParent
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.transformation.private.PrivateResize import PrivateResize
from super_scad.type.Size2 import Size2


class Resize2D(ScadSingleChildParent):
    """
    Modifies the size of the child widget to match the given width and depth. See
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#resize.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 new_size: Size2 | None = None,
                 new_width: float | None = None,
                 new_depth: float | None = None,
                 auto: bool | Tuple[bool, bool] | None = None,
                 auto_width: bool | None = None,
                 auto_depth: bool | None = None,
                 convexity: int | None = None,
                 child: ScadWidget):
        """
        Object constructor.

        :param new_size: The new_size along all two axes.
        :param new_width: The new width (the new size along the x-axis).
        :param new_depth: The new depth (the new size along the y-axis).
        :param auto: Whether to auto-scale any 0-dimensions to match.
        :param convexity: Number of "inward" curves, i.e. expected number of path crossings of an arbitrary line through
                          the child widget.
        :param child: The child widget to be resized.
        """
        ScadSingleChildParent.__init__(self, args=locals(), child=child)

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        admission = ArgumentAdmission(self._args)
        admission.validate_exclusive({'new_size'}, {'new_width', 'new_depth'})
        admission.validate_exclusive({'auto'}, {'auto_width', 'auto_depth'})

        # Handle resizing beyond resolution.

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def new_size(self) -> Size2:
        """
        Returns the new_size along all three axes.
        """
        return Size2(self.new_width, self.new_depth)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def new_width(self) -> float:
        """
        Returns new width (the new size along the x-axis).
        """
        if 'new_size' in self._args:
            return self.uc(self._args['new_size'].width)

        return self.uc(self._args.get('new_width', 0.0))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def new_depth(self) -> float:
        """
        Returns the new depth (the new size along the y-axis).
        """
        if 'new_size' in self._args:
            return self.uc(self._args['new_size'].depth)

        return self.uc(self._args.get('new_depth', 0.0))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def auto(self) -> Tuple[bool, bool]:
        """
        Returns whether to auto-scale the width and depth.
        """
        return self.auto_width, self.auto_depth

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def auto_width(self) -> bool:
        """
        Returns whether to auto-scale the width (the size along the x-axis).
        """
        if round(self.new_width, 4) == 0.0:  # xxx Use rounding in target units.
            if 'auto' in self._args:
                if isinstance(self._args['auto'], tuple):
                    return self._args['auto'][0]
                else:
                    return self._args['auto']

            if 'auto_width' in self._args:
                return self._args['auto_width']

        return False

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def auto_depth(self) -> bool:
        """
        Returns whether to auto-scale the depth (the size along the y-axis).
        """
        if round(self.new_depth, 4) == 0.0:  # xxx Use rounding in target units.
            if 'auto' in self._args:
                if isinstance(self._args['auto'], tuple):
                    return self._args['auto'][1]
                else:
                    return self._args['auto']

            if 'auto_depth' in self._args:
                return self._args['auto_depth']

        return False

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def convexity(self) -> int | None:
        """
        Returns the convexity.
        """
        return self._args.get('convexity')

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        return PrivateResize(new_size=self.new_size, auto=self.auto, convexity=self.convexity, child=self.child)

# ----------------------------------------------------------------------------------------------------------------------
