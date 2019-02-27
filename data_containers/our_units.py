"""All data that are related to units on our possession are here"""
from sc2.constants import DRONE, HYDRALISK, LARVA, MUTALISK, OVERLORD, OVERSEER, QUEEN, ULTRALISK, ZERGLING


class OurUnitsData:
    """This is the data container for all our units"""

    def __init__(self):
        self.overlords = self.drones = self.queens = self.zerglings = self.larvae = self.overseers = None
        self.mutalisks = self.hydras = self.ultralisks = None
        self.burrowed_lings = []

    def initialize_hatchery_units(self):
        """Initialize all our buildings(hatchery tech)"""
        self.overlords = self.units(OVERLORD)
        self.drones = self.units(DRONE)
        self.queens = self.units(QUEEN)
        self.zerglings = (
            self.units(ZERGLING).tags_not_in(self.burrowed_lings) if self.burrowed_lings else self.units(ZERGLING)
        )
        self.larvae = self.units(LARVA)

    def initialize_hive_units(self):
        """Initialize all our buildings (hive tech)"""
        self.ultralisks = self.units(ULTRALISK)

    def initialize_lair_units(self):
        """Initialize all our buildings(lair tech)"""
        self.overseers = self.units(OVERSEER)
        self.mutalisks = self.units(MUTALISK)
        self.hydras = self.units(HYDRALISK)
