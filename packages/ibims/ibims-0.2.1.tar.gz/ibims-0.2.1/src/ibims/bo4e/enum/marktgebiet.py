from enum import Enum


class Marktgebiet(str, Enum):
    """
    a strenum where the str-value of each member is the ILN of the Regelzone for Gas
    Also known as: Marktgebietscode
    """

    FIELD_37_Y005053_MH0000_R = "37Y005053MH0000R"
    THE0_BFH027950000 = "THE0BFH027950000"
    THE0_BFL027960000 = "THE0BFL027960000"
