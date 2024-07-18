from abc import ABC, abstractmethod
from typing import List, Tuple

from super_scad.scad.Unit import Unit
from super_scad.type.Point2 import Point2

from super_scad_thread.enum.ThreadAnatomy import ThreadAnatomy


class ThreadProfileCreator(ABC):
    """
    Abstract parent class for creating thread profiles.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 *,
                 pitch: float):
        """
        Object constructor.

        :param pitch: The pitch of the thread.
        """

        self.__pitch: float = pitch
        """
        The pitch of the thread.
        """

        self.__master_profile: List[Tuple[ThreadAnatomy, Point2]] | \
                               Tuple[Tuple[ThreadAnatomy, Point2], ...] | None = None
        """
        The 2D master profile of the thread. I.e. all the 2D points of the profile for one pitch.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def pitch(self) -> float:
        """
        Return the pitch of the thread.
        """
        return self.__pitch

    # ------------------------------------------------------------------------------------------------------------------
    @property
    @abstractmethod
    def unit_of_length(self) -> Unit:
        """
        Returns the unit of length in which the thread is specified.
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def number_of_points_per_pitch(self) -> int:
        """
        Returns the number of points for one pitch.
        """
        if self.__master_profile is None:
            self.__master_profile = self.create_master_profile

        return len(self.__master_profile)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    @abstractmethod
    def minor_diameter(self) -> float:
        """
        Returns the minor diameter of the thread.
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    @property
    @abstractmethod
    def major_diameter(self) -> float:
        """
        Returns the major diameter of the thread.
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def create_master_profile(self) -> List[Tuple[ThreadAnatomy, Point2]] | \
                                       Tuple[Tuple[ThreadAnatomy, Point2], ...]:
        """
        Returns the 2D master profile of the thread. I.e. all the 2D points of the profile for one pitch. The thread
        profile must start in the middel of the root.
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    def create_thread_profile(self, length: float) -> Tuple[List[ThreadAnatomy], List[Point2]]:
        """
        Returns the thread profile points.
        """
        if self.__master_profile is None:
            self.__master_profile = self.create_master_profile()

        anatomy = []
        points = []

        if self.__master_profile[0][1].y != 0.0:
            anatomy.append(self.__master_profile[0][0])
            points.append(Point2(self.__master_profile[0][1].x, -self.__pitch))

        for revolution in range(-1, int(length / self.__pitch) + 2):
            for j in range(0, len(self.__master_profile)):
                x = self.__master_profile[j][1].x
                y = self.__master_profile[j][1].y + revolution * self.__pitch
                if y <= (length + self.__pitch):
                    anatomy.append(self.__master_profile[j][0])
                    points.append(Point2(x, y))

        return anatomy, points

# ----------------------------------------------------------------------------------------------------------------------
