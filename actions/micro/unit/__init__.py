""" Group all classes from micro/unit"""
from . import changeling_control, creep_tumor, drone_control, overlord_control, overseer_control, queen_control


def get_macro_units_commands(cmd):
    """ Getter for all commands from micro/unit"""
    return (
        changeling_control.ChangelingControl(cmd),
        creep_tumor.CreepTumor(cmd),
        drone_control.DroneControl(cmd),
        overlord_control.OverlordControl(cmd),
        overseer_control.OverseerControl(cmd),
        queen_control.QueenControl(cmd),
    )
