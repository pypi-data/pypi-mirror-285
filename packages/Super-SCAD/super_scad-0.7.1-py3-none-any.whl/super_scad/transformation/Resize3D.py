from typing import Tuple

from super_scad.scad.ArgumentAdmission import ArgumentAdmission
from super_scad.scad.Context import Context
from super_scad.scad.ScadSingleChildParent import ScadSingleChildParent
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.transformation.private.PrivateResize import PrivateResize
from super_scad.type.Size3 import Size3


class Resize3D(ScadSingleChildParent):
    """
    Modifies the size of the child widget to match the given width, depth, and height. See
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Transformations#resize.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 new_size: Size3 | None = None,
                 new_width: float | None = None,
                 new_depth: float | None = None,
                 new_height: float | None = None,
                 auto: bool | Tuple[bool, bool, bool] | None = None,
                 auto_width: bool | None = None,
                 auto_depth: bool | None = None,
                 auto_height: bool | None = None,
                 convexity: int | None = None,
                 child: ScadWidget) -> None:
        """
        Object constructor.

        :param new_size: The new_size along all two axes.
        :param new_width: The new width (the new size along the x-axis).
        :param new_depth: The new depth (the new size along the y-axis).
        :param new_height: The new height size (the new size along the z-axis).
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
        admission.validate_exclusive({'new_size'}, {'new_width', 'new_depth', 'new_height'})
        admission.validate_exclusive({'auto'}, {'auto_width', 'auto_depth', 'auto_height'})
        admission.validate_required({'new_width', 'new_size', 'auto_width', 'auto'},
                                    {'new_depth', 'new_size', 'auto_depth', 'auto'},
                                    {'new_height', 'new_size', 'auto_height', 'auto'})

        # Handle resizing beyond resolution.

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def new_size(self) -> Size3:
        """
        Returns the new_size along all three axes.
        """
        return Size3(self.new_width, self.new_depth, self.new_height)

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
    def new_height(self) -> float:
        """
        Returns the new height (the new size along the z-axis).
        """
        if 'new_size' in self._args:
            return self.uc(self._args['new_size'].height)

        return self.uc(self._args.get('new_height', 0.0))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def auto(self) -> Tuple[bool, bool, bool]:
        """
        Returns whether to auto-scale the width, depth and height.
        """
        return self.auto_width, self.auto_depth, self.auto_height

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
    def auto_height(self) -> bool:
        """
        Returns whether to auto-scale the height (the size along the z-axis).
        """
        if round(self.new_height, 4) == 0.0:  # xxx Use rounding in target units.
            if 'auto' in self._args:
                if isinstance(self._args['auto'], tuple):
                    return self._args['auto'][2]
                else:
                    return self._args['auto']

            if 'auto_height' in self._args:
                return self._args['auto_height']

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
