from enum import Enum


class Regelzone(str, Enum):
    """
    a strenum where the str-value of each member is the ILN of the Regelzone for electricity
    """

    FIELD_10_YDE_ENBW_____N = "10YDE-ENBW-----N"
    FIELD_10_YDE_EON______1 = "10YDE-EON------1"
    FIELD_10_YDE_RWENET___I = "10YDE-RWENET---I"
    FIELD_10_YDE_VE_______2 = "10YDE-VE-------2"
