from enum import auto, Enum, STRICT


class ThreadAnatomy(Enum, boundary=STRICT):
    """
    Enumeration of all possible locations of a point on a thread profile.
    """
    # ------------------------------------------------------------------------------------------------------------------
    AT_MINOR = auto()
    """
    For external thread the point is at the root.
    For internal thread the point is at the crest.
    """

    AT_MAJOR = auto()
    """
    For external thread the point is at the crest.
    For internal thread the point is at the root.
    """

    AT_FLANK = auto()
    """
    The point is on a flank of the thread.
    """

# ----------------------------------------------------------------------------------------------------------------------
