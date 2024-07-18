import math
from abc import ABC
from typing import List, Tuple

from super_scad.d3.Polyhedron import Polyhedron
from super_scad.scad import Length
from super_scad.scad.Context import Context
from super_scad.scad.ScadWidget import ScadWidget
from super_scad.transformation.Mirror3D import Mirror3D
from super_scad.transformation.Translate3D import Translate3D
from super_scad.type.Angle import Angle
from super_scad.type.Point2 import Point2
from super_scad.type.Point3 import Point3
from super_scad.util.Radius2Sides4n import Radius2Sides4n

from super_scad_thread.enum.ThreadAnatomy import ThreadAnatomy
from super_scad_thread.enum.ThreadDirection import ThreadDirection
from super_scad_thread.lead_thread.ThreadLeadCreator import ThreadLeadCreator
from super_scad_thread.ThreadProfileCreator import ThreadProfileCreator


class Thread(ScadWidget, ABC):
    """
    Abstract SuperSCAD widget for creating threads.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def _validate_arguments(self) -> None:
        """
        Validates the arguments supplied to the constructor of this SuperSCAD widget.
        """
        assert self.length > 0.0, f'Length must be greater than 0. Got length {self.length}'
        assert isinstance(self.thread_profile_creator, ThreadProfileCreator)
        assert isinstance(self.top_thread_lead_creator, ThreadLeadCreator)
        assert isinstance(self.bottom_thread_lead_creator, ThreadLeadCreator)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def center(self) -> bool:
        """
        Returns whether to center the thread along the z-axis.
        """
        return self._args.get('center', False)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def length(self) -> float:
        """
        Returns the length of the thread.
        """
        return self.uc(self._args['length'])

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def minor_diameter(self) -> float:
        """
        Returns the minor diameter of the thread.
        """
        return Length.convert(self.thread_profile_creator.minor_diameter,
                              self.thread_profile_creator.unit_of_length,
                              Context.get_unit_length_current())

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def major_diameter(self) -> float:
        """
        Returns the major diameter of the thread.
        """
        return Length.convert(self.thread_profile_creator.major_diameter,
                              self.thread_profile_creator.unit_of_length,
                              Context.get_unit_length_current())

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def thread_profile_creator(self) -> ThreadProfileCreator:
        """
        Returns the thread profile creator.
        """
        return self._args['thread_profile_creator']

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def top_thread_lead_creator(self) -> ThreadLeadCreator:
        """
        Returns the object for creating a lead on the top of the thread.
        """
        return self._args['top_thread_lead_creator']

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def bottom_thread_lead_creator(self) -> ThreadLeadCreator:
        """
        Returns the object for creating a lead on the bottom of the thread.
        """
        return self._args['bottom_thread_lead_creator']

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def direction(self) -> ThreadDirection:
        """
        Returns direction of the thread.
        """
        return self._args['direction']

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def convexity(self) -> int:
        """
        Returns the convexity of the thread.
        """
        return self._args['convexity']

    # ------------------------------------------------------------------------------------------------------------------
    def _create_faces(self, thread_3d: List[List[Point3]]) -> List[List[Point3] | Tuple[Point3, ...]]:
        """
        Creates faces given a thread profile in 3D.

        :param thread_3d: The thread profile in 3D.
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __thread_translate(master_thread_profile_2d: List[Point2], z: float) -> List[Point2]:
        """
        Apply the translation in the z-axis direction due to rotation.

        :param master_thread_profile_2d: The master thread profile in 2D.
        :param z: The translation in z-axis direction.
        """
        thread_profile_2d = []
        for key, point in enumerate(master_thread_profile_2d):
            thread_profile_2d.append(Point2(point.x, point.y + z))

        return thread_profile_2d

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __thread_move_point_to_zero(thread_profile_2d: List[Point2]) -> List[Point2]:
        """
        Moves a thread profile point just below the zero y-axis at y=0.0 without modifying the profile.

        :param thread_profile_2d: The master thread profile in 2D.
        """
        found = False
        index = 0
        for index in range(1, len(thread_profile_2d)):
            if thread_profile_2d[index - 1].y < 0.0 < thread_profile_2d[index].y:
                found = True
                break
            elif thread_profile_2d[index].y > 0.0:
                break

        if found:
            try:
                m = ((thread_profile_2d[index - 1].y - thread_profile_2d[index].y) /
                     (thread_profile_2d[index - 1].x - thread_profile_2d[index].x))
                x = thread_profile_2d[index - 1].x - thread_profile_2d[index - 1].y * m
                thread_profile_2d[index - 1] = Point2(x, 0.0)
            except ZeroDivisionError:
                thread_profile_2d[index - 1] = Point2(thread_profile_2d[index - 1].x, 0.0)

        return thread_profile_2d

    # ------------------------------------------------------------------------------------------------------------------
    def __thread_create_lead(self,
                             thread_profile: List[Point2],
                             thread_anatomy: List[ThreadAnatomy],
                             z: float,
                             angle: float,
                             lead_creator: ThreadLeadCreator) -> List[Point2]:
        """
        Applies the tread lead transformation on the thread profile in 2D.

        :param thread_profile: The thread profile in 2D.
        :param thread_anatomy: The location of a points on the thread profile.
        :param z: The current translation in z-axis direction.
        :param angle: The rotation in degrees.
        :param lead_creator: The thread lead creator.
        """
        thread_profile = lead_creator.create_lead(thread_profile, thread_anatomy, z, angle)

        self.__thread_assert_lead(thread_profile)

        return thread_profile

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __thread_assert_lead(thread_profile_2d: List[Point2]) -> None:
        """
        Assets the thread after applying a lead in or our.

        :param thread_profile_2d: The master thread profile in 2D.
        """
        assert thread_profile_2d[0].y == 0.0, f'The first point of a thread profile must at y=0.0 zero' \
                                              ', got {thread_profile_2d[0]}'
        for point in thread_profile_2d:
            assert point.y >= 0.0, 'All points of a thread profile must be at y>=0.0'

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __thread_reverse(thread_profile_2d: List[Point2], length: float) -> List[Point2]:
        """
        Reverse the thread profile and align the (original) top at z=0.0.

        :param thread_profile_2d: The thread profile in 2D.
        :param length: The (final) length of the thread.
        """
        reversed_thread_profile = []
        for key, point in enumerate(reversed(thread_profile_2d)):
            reversed_thread_profile.append(Point2(point.x, length - point.y))

        return reversed_thread_profile

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __thread_transform_to_3d(thread_profile_2d: List[Point2], angle: float) -> List[Point3]:
        """
        Apply the transformation form 2D profile to a 3D profile

        :param thread_profile_2d: The thread profile in 2D.
        :param angle: The rotation in degrees.
        """
        thread_profile_3d = []
        for point in thread_profile_2d:
            x = point.x * math.cos(math.radians(angle))
            y = point.x * math.sin(math.radians(angle))
            z = point.y
            thread_profile_3d.append(Point3(x, y, z))

        return thread_profile_3d

    # ------------------------------------------------------------------------------------------------------------------
    def build(self, context: Context) -> ScadWidget:
        """
        Builds a SuperSCAD widget.

        :param context: The build context.
        """
        thread_profile_creator = self.thread_profile_creator
        context.set_unit_length_current(thread_profile_creator.unit_of_length)

        length = self.length
        master_thread_anatomy, master_thread_profile_2d = thread_profile_creator.create_thread_profile(length)
        master_thread_anatomy_reversed = list(reversed(master_thread_anatomy))
        pitch = thread_profile_creator.pitch

        top_thread_lead_creator = self.top_thread_lead_creator
        bottom_thread_lead_creator = self.bottom_thread_lead_creator

        # Offsets for the top end due to inversion of the thread.
        angle_offset = 360.0 * math.remainder(length, pitch)
        z_offset = pitch * angle_offset / 360.0

        thread_3d = []
        sides = Radius2Sides4n.r2sides4n(context, thread_profile_creator.major_diameter / 2.0)
        for i in range(0, sides):
            z = i * pitch / sides
            angle = i * 360.0 / sides
            thread_profile_2d = self.__thread_translate(master_thread_profile_2d, z)
            thread_profile_2d = self.__thread_move_point_to_zero(thread_profile_2d)
            thread_profile_2d = self.__thread_create_lead(thread_profile_2d,
                                                          master_thread_anatomy,
                                                          z,
                                                          angle,
                                                          bottom_thread_lead_creator)
            thread_profile_2d = self.__thread_reverse(thread_profile_2d, length)
            thread_profile_2d = self.__thread_move_point_to_zero(thread_profile_2d)
            thread_profile_2d = self.__thread_create_lead(thread_profile_2d,
                                                          master_thread_anatomy_reversed,
                                                          Angle.normalize(z_offset - z, pitch),
                                                          Angle.normalize(angle_offset - angle, 360.0),
                                                          top_thread_lead_creator)
            thread_profile_2d = self.__thread_reverse(thread_profile_2d, length)
            thread_profile_3d = self.__thread_transform_to_3d(thread_profile_2d, angle)
            thread_3d.append(thread_profile_3d)

        faces = self._create_faces(thread_3d)
        polyhedron = Polyhedron(faces=faces, highlight_face=None, highlight_diameter=0.1, convexity=self.convexity)

        if self.direction == ThreadDirection.LEFT:
            polyhedron = Mirror3D(x=1.0, child=polyhedron)

        if self.center:
            polyhedron = Translate3D(z=-self.length / 2.0, child=polyhedron)

        return polyhedron

# ----------------------------------------------------------------------------------------------------------------------
