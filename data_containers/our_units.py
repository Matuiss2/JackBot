"""All data that are related to units on our possession are here"""
from sc2.constants import UnitTypeId


class OurUnitsData:
    """This is the data container for all our units"""

    def __init__(self):
        self.overlords = self.drones = self.queens = self.zerglings = self.larvae = self.overseers = None
        self.mutalisks = self.hydras = self.ultralisks = None

    def initialize_hatchery_units(self):
        """Initialize all our buildings(hatchery tech)"""
        self.overlords = self.units(UnitTypeId.OVERLORD)
        self.drones = self.units(UnitTypeId.DRONE)
        self.queens = self.units(UnitTypeId.QUEEN)
        self.zerglings = self.units(UnitTypeId.ZERGLING)
        self.larvae = self.units(UnitTypeId.LARVA)

    def initialize_hive_units(self):
        """Initialize all our buildings (hive tech)"""
        self.ultralisks = self.units(UnitTypeId.ULTRALISK)

    def initialize_lair_units(self):
        """Initialize all our buildings(lair tech)"""
        self.overseers = self.units(UnitTypeId.OVERSEER)
        self.mutalisks = self.units(UnitTypeId.MUTALISK)
        self.hydras = self.units(UnitTypeId.HYDRALISK)
