from abc import ABC
from typing import List

from super_scad.type.Point2 import Point2

from super_scad_thread.enum.ThreadAnatomy import ThreadAnatomy


class ThreadLeadCreator(ABC):
    """
    Creates a lead thread on a 2D thread profile.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def create_lead(self,
                    thread_profile: List[Point2],
                    thread_anatomy: List[ThreadAnatomy],
                    z: float,
                    angle: float) -> List[Point2]:
        """
        Creates a lead thread on a 2D thread profile.

        :param thread_profile: The thread profile in 2D.
        :param thread_anatomy: The location of a points on the thread profile.
        :param z: The current translation in z-axis direction.
        :param angle: The angle of the current rotation.

        It is guaranteed that 0.0 <= z < pitch.
        It is guaranteed that 0.0 <= angle < 360.0.
        """
        raise NotImplementedError()

# ----------------------------------------------------------------------------------------------------------------------
