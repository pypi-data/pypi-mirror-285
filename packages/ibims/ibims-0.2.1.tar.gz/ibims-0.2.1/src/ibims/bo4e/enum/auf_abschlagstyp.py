from enum import Enum


class AufAbschlagstyp(str, Enum):
    """
    Festlegung, ob der Auf- oder Abschlag mit relativen oder absoluten Werten erfolgt.
    """

    RELATIV = "RELATIV"
    ABSOLUT = "ABSOLUT"
