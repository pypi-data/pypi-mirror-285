import itertools
from typing import Dict, Iterable, List, Tuple

from super_scad.boolean.Union import Union
from super_scad.d3.Cylinder import Cylinder
from super_scad.d3.private.PrivatePolyhedron import PrivatePolyhedron
from super_scad.d3.Sphere import Sphere
from super_scad.scad.Context import Context
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.transformation.Paint import Paint
from super_scad.transformation.Translate3D import Translate3D
from super_scad.type.Color import Color
from super_scad.type.Point3 import Point3


class Polyhedron(ScadWidget):
    """
    Widget for creating polyhedrons. See https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Primitive_Solids#polyhedron.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 faces: List[List[Point3] | Tuple[Point3, ...]],
                 highlight_face: int | None = None,
                 highlight_diameter: float | None = None,
                 convexity: int | None = None):
        """
        Object constructor.

        :param faces:  The faces that collectively enclose the solid.
        :param highlight_face: The index of the face to highlight. Each point of the face is marked, the first point is
                           colored red, the second orange, the third green, and all other points are color black.
        :param highlight_diameter: The diameter of the spheres that highlight the nodes of the faces.
        :param convexity: Number of "inward" curves, i.e. expected number of path crossings of an arbitrary line through
                          the polyhedron.

        Each face consists of 3 or more points. Faces may be defined in any order, but the points of each face must be
        ordered correctly, must be ordered in clockwise direction when looking at each face from outside inward. Define
        enough faces to fully enclose the solid, with no overlap. If points that describe a single face are not on the
        same plane, the face is by OpenSCAD automatically split into triangles as needed.
        """
        ScadWidget.__init__(self, args=locals())

        for key, face in enumerate(faces):
            assert len(face) >= 3, f'Each face must have 3 or more points. Face {key} as only {len(face)} points'

        if highlight_face is not None:
            assert highlight_face < len(
                    faces), f'Can not highlight face {highlight_face} as the polyhedron has only {len(faces)} points'

        self.__real_faces: List[List[int]] = []
        """
        The real faces of the polyhedron.
        """

        self.__distinct_points: List[Point3] = []
        """
        The distinct points of the polyhedron.
        """

        self.__map_faces_real_faces: Dict[int, int] = {}
        """
        The map from the keys of the given faces to kes of the real faces.
        """

        self.__is_ready: bool = False
        """
        Whether the faces and the points have been computed. 
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def highlight_face(self) -> int | None:
        """
        Returns the index of the face to highlight
        """
        return self._args.get('highlight_face')

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def highlight_diameter(self) -> float | None:
        """
        Returns the diameter of the spheres that highlight the nodes of the faces.
        """
        return self._args.get('highlight_diameter')

    # ------------------------------------------------------------------------------------------------------------------
    def real_highlight_diameter(self, context: Context) -> float:
        """
        Returns the real diameter of the spheres that highlight the nodes of the faces.
        """
        diameter = self.highlight_diameter
        if diameter is not None:
            return max(diameter, 5.0 * context.resolution)

        face = self._args['faces'][self.highlight_face]

        total_distance = 0.0
        prev_point = None
        for point in face:
            if prev_point is not None:
                total_distance += (point - prev_point).length
            prev_point = point

        if prev_point is not None:
            total_distance += (face[0] - prev_point).length

        average_distance = total_distance / (len(face) + 1)
        diameter = 0.1 * average_distance

        return self.uc(max(diameter, 5.0 * context.resolution))

    # ------------------------------------------------------------------------------------------------------------------
    def real_points(self, context: Context) -> List[Point3]:
        """
        Returns the real points of the polyhedron.
        """
        if not self.__is_ready:
            self.__prepare_data(context)

        return self.uc(self.__distinct_points)

    # ------------------------------------------------------------------------------------------------------------------
    def real_faces(self, context: Context) -> List[List[int]]:
        """
        Returns the real faces of the polyhedron.
        """
        if not self.__is_ready:
            self.__prepare_data(context)

        return self.__real_faces

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def convexity(self) -> int | None:
        """
        Returns the number of "inward" curves, i.e. expected number of path crossings of an arbitrary line through the
        child widget.
        """
        return self._args.get('convexity')

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __clean_face(face: List[int]) -> List[int] | None:
        """
        Removes fused point from a face. If face has only two or fewer points, returns None.

        @param face: The face.
        """
        new_face = [key for key, _g in itertools.groupby(face)]
        if new_face[0] == new_face[-1]:
            new_face.pop()

        if len(new_face) >= 3:
            return new_face

        return None

    # ------------------------------------------------------------------------------------------------------------------
    def __pass1(self, context: Context) -> None:
        """
        Pass 1: Remove fused points and enumerate points in faces.

        @param context: The build context.
        """
        digits = context.length_digits

        distinct_point_map = {}
        self.__distinct_points = []
        self.__real_faces = []
        for key, face in enumerate(self._args['faces']):
            new_face = []
            for point in face:
                point_rounded = Point3(round(float(point.x), digits),
                                       round(float(point.y), digits),
                                       round(float(point.z), digits))
                point_str = str(point_rounded)
                index = distinct_point_map.get(point_str)
                if index is None:
                    index = len(self.__distinct_points)
                    distinct_point_map[point_str] = index
                    self.__distinct_points.append(point_rounded)
                new_face.append(index)

            if self.__clean_face(new_face) is not None:
                self.__real_faces.append(new_face)
                self.__map_faces_real_faces[key] = len(self.__real_faces) - 1

    # ------------------------------------------------------------------------------------------------------------------
    def __pass2(self):
        """
        Pass 2: Remove unused points and renumber points.
        """
        point_keys = set()
        for face in self.__real_faces:
            point_keys.update(face)

        if len(point_keys) == len(self.__distinct_points):
            return

        new_points = []
        key_map = {}
        for key, point in enumerate(self.__distinct_points):
            if key in point_keys:
                new_points.append(point)
                key_map[key] = len(new_points) - 1
        self.__distinct_points = new_points

        for key, face in enumerate(self.__real_faces):
            new_face = []
            for index in face:
                new_face.append(key_map[index])
            self.__real_faces[key] = new_face

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __crate_markers_nodes(face: Iterable[Point3], is_real_face: bool, diameter: float) -> List[ScadWidget]:
        """
        Create markers of the nodes of a face.

        :param face: The face.
        :param is_real_face: Whether the face is a real face.
        :param diameter: The diameter of the markers.
        """
        nodes = []
        for key, point in enumerate(face):
            if is_real_face:
                if key == 0:
                    color = Color('red')
                elif key == 1:
                    color = Color('orange')
                elif key == 2:
                    color = Color('green')
                else:
                    color = Color('black')
            else:
                color = Color('pink')

            node = Paint(color=color,
                         child=Translate3D(vector=point,
                                           child=Sphere(diameter=diameter, fn=16)))
            nodes.append(node)

        return nodes

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __crate_markers_edges(face: Iterable[Point3],
                              is_real_face: bool,
                              diameter: float,
                              context: Context) -> List[ScadWidget]:
        """
        Create markers of the edges of a face.

        :param face: The face.
        :param is_real_face: Whether the face is a real face.
        :param diameter: The diameter of cylinders on the edges.
        :param context: The build context.
        """
        if is_real_face:
            color = Color('black')
        else:
            color = Color('pink')

        edges = []
        prev_point = None
        first_point = None
        for key, point in enumerate(face):
            if prev_point is None:
                first_point = point
            else:
                if (point - prev_point).length >= context.resolution:
                    edge = Paint(color=color,
                                 child=Cylinder(start_point=prev_point,
                                                end_point=point,
                                                diameter=diameter,
                                                fn=16))
                    edges.append(edge)

            prev_point = point

        if prev_point is not None and first_point is not None:
            if (first_point - prev_point).length >= context.resolution:
                edge = Paint(color=color,
                             child=Cylinder(start_point=prev_point,
                                            end_point=first_point,
                                            diameter=diameter))
                edges.append(edge)

        return edges

    # ------------------------------------------------------------------------------------------------------------------
    def __crate_markers(self, context: Context) -> Tuple[List[ScadWidget], List[ScadWidget]]:
        """
        Create markers to highlight a face.

        :param context: The build context.
        """
        diameter_node = self.real_highlight_diameter(context)
        diameter_edge = 0.2 * diameter_node

        if self.highlight_face in self.__map_faces_real_faces:
            real_face = self.__real_faces[self.__map_faces_real_faces[self.highlight_face]]
            face = []
            for key in real_face:
                face.append(self.__distinct_points[key])
            is_real_face = True
        else:
            face = self._args['faces'][self.highlight_face]
            is_real_face = False
        nodes = self.__crate_markers_nodes(face, is_real_face, diameter_node)
        edges = self.__crate_markers_edges(face, is_real_face, diameter_edge, context)

        return nodes, edges

    # ------------------------------------------------------------------------------------------------------------------
    def __prepare_data(self, context):
        """
        Prepares the data as expected by OpenSCAD polyhedron.

        @param context: The build context.
        """
        self.__pass1(context)
        self.__pass2()

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        self.__prepare_data(context)

        polyhedron = PrivatePolyhedron(points=self.real_points(context),
                                       faces=self.real_faces(context),
                                       convexity=self.convexity)

        if self.highlight_face is None:
            return polyhedron

        markers = self.__crate_markers(context)

        return Union(children=[polyhedron] + markers[0] + markers[1])

# ----------------------------------------------------------------------------------------------------------------------
