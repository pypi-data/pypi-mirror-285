from enum import Enum


class Rollencodetyp(str, Enum):
    """
    Gibt den Codetyp einer Rolle, beispielsweise einer Marktrolle, an.
    """

    BDEW = "BDEW"
    DVGW = "DVGW"
    GLN = "GLN"
