""" Group all classes from micro/unit"""
from . import creep_tumor, drone_control, overlord_control, overseer_control, queen_control


def get_macro_units_commands(command):
    """ Getter for all commands from micro/unit"""
    return (
        creep_tumor.CreepTumor(command),
        drone_control.DroneControl(command),
        overlord_control.OverlordControl(command),
        overseer_control.OverseerControl(command),
        queen_control.QueenControl(command),
    )
