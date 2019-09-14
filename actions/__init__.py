""" Group all unit commands"""
from .anti_cheese import get_cheese_defense_commands
from .micro import get_army_and_building_commands
from .micro.unit import get_macro_units_commands


def get_unit_commands(cmd):
    """ Getter for all unit commands"""
    return get_macro_units_commands(cmd) + get_army_and_building_commands(cmd) + get_cheese_defense_commands(cmd)
