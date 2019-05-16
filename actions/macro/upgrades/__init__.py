""" Group all classes from macro/upgrades"""
from . import cavern_upgrades, evochamber_upgrades, hydraden_upgrades, spawning_pool_upgrades


def get_upgrade_commands(cmd):
    """ Getter for all commands from macro/upgrades"""
    return (
        cavern_upgrades.CavernUpgrades(cmd),
        evochamber_upgrades.EvochamberUpgrades(cmd),
        # hydraden_upgrades.HydradenUpgrades(cmd),
        spawning_pool_upgrades.SpawningPoolUpgrades(cmd),
    )
