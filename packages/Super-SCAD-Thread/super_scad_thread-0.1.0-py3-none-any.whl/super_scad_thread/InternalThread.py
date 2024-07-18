import math
from typing import List, Tuple

from super_scad.scad.ArgumentAdmission import ArgumentAdmission
from super_scad.type.Point3 import Point3

from super_scad_thread.enum.ThreadDirection import ThreadDirection
from super_scad_thread.lead_thread.internal.InternalThreadLeadCreator import InternalThreadLeadCreator
from super_scad_thread.lead_thread.ThreadLeadCreator import ThreadLeadCreator
from super_scad_thread.Thread import Thread
from super_scad_thread.ThreadProfileCreator import ThreadProfileCreator


class InternalThread(Thread):
    """
    SuperSCAD widget for creating internal threads.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 length: float,
                 thread_profile_creator: ThreadProfileCreator,
                 top_thread_lead_creator: ThreadLeadCreator,
                 bottom_thread_lead_creator: ThreadLeadCreator,
                 direction: ThreadDirection = ThreadDirection.RIGHT,
                 outer_radius: float | None = None,
                 outer_diameter: float | None = None,
                 center: bool | None = None,
                 convexity: int = 2):
        """
        Object contructor.

        :param length: The length of the thread.
        :param thread_profile_creator: The thread profile creator.
        :param top_thread_lead_creator: The object for creating a lead on the top of the thread.
        :param bottom_thread_lead_creator: The object for creating a lead on the top of the thread.
        :param direction: The direction of the thread.
        :param outer_radius: The outer radius of the thread.
        :param outer_diameter: The outer diameter of the thread.
        :param center: Whether to center the thread along the z-axis.
        :param convexity: The convexity of the thread. Normally 2 is enough, however, in some cases a higher value is
                          required.
        """
        Thread.__init__(self, args=locals())

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        Thread._validate_arguments(self)

        admission = ArgumentAdmission(self._args)
        admission.validate_exclusive({'outer_radius'}, {'outer_diameter'})
        admission.validate_required({'outer_radius', 'outer_diameter'})

        assert isinstance(self.top_thread_lead_creator, InternalThreadLeadCreator)
        assert isinstance(self.bottom_thread_lead_creator, InternalThreadLeadCreator)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def outer_radius(self) -> float:
        """
        Returns the internal radius of the external thread.
        """
        radius = None
        if 'outer_radius' in self._args:
            radius = self._args['outer_radius']

        if 'outer_diameter' in self._args:
            radius = self._args['outer_diameter'] / 2.0

        assert radius is not None, 'Radius is mandatory.'

        if radius <= 0.0:
            radius = self.thread_profile_creator.major_diameter / 2.0

        return self.uc(radius)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def outer_diameter(self) -> float:
        """
        Returns the internal diameter of the external thread.
        """
        diameter = None
        if 'outer_radius' in self._args:
            diameter = 2.0 * self._args['outer_radius']

        if 'outer_diameter' in self._args:
            diameter = self._args['outer_diameter']

        assert diameter is not None, 'Diameter is mandatory.'

        if diameter <= 0.0:
            diameter = self.thread_profile_creator.major_diameter

        return self.uc(diameter)

    # ------------------------------------------------------------------------------------------------------------------
    def __create_faces_thread(self,
                              faces: List[List[Point3] | Tuple[Point3, ...]],
                              thread_3d: List[List[Point3]]) -> None:
        """
        Creates the faces for the thread profile.
        
        :param faces: The list of faces.
        :param thread_3d: The thread profile in 3D.
        """
        edges = len(thread_3d)
        number_of_points_per_pitch = self.thread_profile_creator.number_of_points_per_pitch

        face = []
        for index in range(number_of_points_per_pitch + 1):
            face.append(thread_3d[0][index])
        faces.append(face)

        # Faces between the consecutive edges.
        for edge in range(1, edges):
            for key in range(1, len(thread_3d[0])):
                faces.append((thread_3d[edge][key - 1],
                              thread_3d[edge][key],
                              thread_3d[edge - 1][key],
                              thread_3d[edge - 1][key - 1]))

        # Faces between the last and first edges.
        for key in range(1, len(thread_3d[0]) - number_of_points_per_pitch - 1):
            faces.append((thread_3d[0][key + number_of_points_per_pitch - 1],
                          thread_3d[0][key + number_of_points_per_pitch],
                          thread_3d[edges - 1][key],
                          thread_3d[edges - 1][key - 1]))

    # ------------------------------------------------------------------------------------------------------------------
    def __create_faces_outer(self,
                             faces: List[List[Point3] | Tuple[Point3, ...]],
                             thread_3d: List[List[Point3]]) -> None:
        """
        Creates faces for the top, bottom, and outer faces.

        :param faces: The list of faces.
        :param thread_3d: The thread profile in 3D.
        """
        edges = len(thread_3d)
        outer_radius = self.outer_radius / math.cos(math.pi / edges)
        number_of_points_per_pitch = self.thread_profile_creator.number_of_points_per_pitch

        bottom_points = []
        top_points = []
        for edge in range(0, edges):
            angle = edge * 360.0 / edges
            x = outer_radius * math.cos(math.radians(angle))
            y = outer_radius * math.sin(math.radians(angle))
            bottom_points.append(Point3(x, y, 0.0))
            top_points.append(Point3(x, y, self.length))

        # Add bottom face.
        for edge in range(1, edges):
            faces.append((bottom_points[edge - 1],
                          bottom_points[edge],
                          thread_3d[edge][0],
                          thread_3d[edge - 1][0]))
        faces.append((bottom_points[edges - 1],
                      bottom_points[0],
                      thread_3d[0][0],
                      thread_3d[edges - 1][0]))

        # ???
        faces.append((bottom_points[0],
                      thread_3d[0][number_of_points_per_pitch],
                      thread_3d[edges - 1][0]))

        # Add top face.
        for edge in range(1, edges):
            faces.append((thread_3d[edge - 1][len(thread_3d[edge - 1]) - 1],
                          thread_3d[edge][len(thread_3d[edge]) - 1],
                          top_points[edge],
                          top_points[edge - 1]))
        faces.append((thread_3d[edges - 1][len(thread_3d[edges - 1]) - 1],
                      thread_3d[0][len(thread_3d[0]) - 1],
                      top_points[0],
                      top_points[edges - 1]))

        # Add outer faces.
        for edge in range(1, edges):
            faces.append((top_points[edge - 1],
                          top_points[edge],
                          bottom_points[edge],
                          bottom_points[edge - 1]))
        faces.append((top_points[edges - 1],
                      top_points[0],
                      bottom_points[0],
                      bottom_points[edges - 1]))

    # ------------------------------------------------------------------------------------------------------------------
    def _create_faces(self, thread_3d: List[List[Point3]]) -> List[List[Point3] | Tuple[Point3, ...]]:
        """
        Creates faces given a thread profile in 3D.

        :param thread_3d: The thread profile in 3D.
        """
        faces: List[List[Point3] | Tuple[Point3, ...]] = []

        self.__create_faces_thread(faces, thread_3d)
        self.__create_faces_outer(faces, thread_3d)

        return faces

# ----------------------------------------------------------------------------------------------------------------------
