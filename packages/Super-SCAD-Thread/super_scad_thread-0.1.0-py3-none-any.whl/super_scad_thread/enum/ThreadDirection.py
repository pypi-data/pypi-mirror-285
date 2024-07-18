from enum import auto, Enum, STRICT


class ThreadDirection(Enum, boundary=STRICT):
    """
    Enumeration of all possible thread directions.
    """
    # ------------------------------------------------------------------------------------------------------------------
    RIGHT = auto()
    """
    Right-hand thread. Turn clockwise to tighten a.k.a. Righty tighty, lefty loosey.
    """

    LEFT = auto()
    """
    Left-hand thread. Turn counter clockwise to tighten.
    """

# ----------------------------------------------------------------------------------------------------------------------
