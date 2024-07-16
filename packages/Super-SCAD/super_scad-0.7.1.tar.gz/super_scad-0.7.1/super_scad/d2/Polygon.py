from typing import List

from super_scad.d2.private.PrivatePolygon import PrivatePolygon
from super_scad.scad.ArgumentAdmission import ArgumentAdmission
from super_scad.scad.Context import Context
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.type.Point2 import Point2


class Polygon(ScadWidget):
    """
    Widget for creating polygons. See https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Using_the_2D_Subsystem#polygon.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 primary: List[Point2] | None = None,
                 points: List[Point2] | None = None,
                 secondary: List[Point2] | None = None,
                 secondaries: List[List[Point2]] | None = None,
                 convexity: int | None = None):
        """
        Object constructor.

        :param primary: The list of 2D points of the polygon.
        :param points: Alias for primary.
        :param secondary: The secondary path that will be subtracted form the polygon.
        :param secondaries: The secondary paths that will be subtracted form the polygon.
        :param convexity: Number of "inward" curves, i.e. expected number of path crossings of an arbitrary line through
                          the child widget.
        """
        ScadWidget.__init__(self, args=locals())

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        admission = ArgumentAdmission(self._args)
        admission.validate_exclusive({'primary'}, {'points'})
        admission.validate_exclusive({'secondary'}, {'secondaries'})
        admission.validate_required({'primary', 'points'})

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def primary(self) -> List[Point2]:
        """
        Returns the points of the polygon.
        """
        return self.uc(self._args.get('primary', self._args.get('points')))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def secondaries(self) -> List[List[Point2]] | None:
        """
        Returns the points of the polygon.
        """
        if 'secondaries' in self._args:
            tmp = []
            for points in self._args['secondaries']:
                tmp.append(self.uc(points))

            return tmp

        if 'secondary' in self._args:
            return [self.uc(self._args['secondary'])]

        return None

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def convexity(self) -> int | None:
        """
        Returns the convexity of the polygon.
        """
        return self._args.get('convexity')

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        secondaries = self.secondaries
        if secondaries is None:
            return PrivatePolygon(points=self.primary, convexity=self.convexity)

        points = self.primary
        n = 0
        m = n + len(points)
        paths = [list(range(n, m))]
        n = m

        for secondary in secondaries:
            m = n + len(secondary)
            points += secondary
            paths.append(list(range(n, m)))
            n = m

        return PrivatePolygon(points=points, paths=paths, convexity=self.convexity)

# ----------------------------------------------------------------------------------------------------------------------
