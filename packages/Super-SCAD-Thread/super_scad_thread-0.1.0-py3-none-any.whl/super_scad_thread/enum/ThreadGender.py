from enum import auto, Enum, STRICT


class ThreadGender(Enum, boundary=STRICT):
    """
    Enumeration of all possible thread genders.
    """
    # ------------------------------------------------------------------------------------------------------------------
    EXTERNAL = auto()
    """
    External thread a.k.a, male thread.
    """

    INTERNAL = auto()
    """
    Internal thread a.k.a, female thread.
    """

# ----------------------------------------------------------------------------------------------------------------------
