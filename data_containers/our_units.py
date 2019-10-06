"""All data that are related to units on our possession are here"""
from sc2.constants import UnitTypeId


class OurUnitsData:
    """This is the data container for all our units"""

    def __init__(self):
        self.changelings = self.drones = self.hydras = self.larvae = self.mutalisks = self.overlords = None
        self.overseers = self.queens = self.ultralisks = self.zerglings = None
        self.changeling_types = {
            UnitTypeId.CHANGELING,
            UnitTypeId.CHANGELINGMARINE,
            UnitTypeId.CHANGELINGMARINESHIELD,
            UnitTypeId.CHANGELINGZEALOT,
            UnitTypeId.CHANGELINGZERGLING,
            UnitTypeId.CHANGELINGZERGLINGWINGS,
        }

    def hatchery_units(self):
        """Initialize all our buildings(hatchery tech)"""
        self.changelings = self.units.of_type(self.changeling_types)
        self.drones = self.units(UnitTypeId.DRONE)
        self.larvae = self.units(UnitTypeId.LARVA)
        self.overlords = self.units(UnitTypeId.OVERLORD)
        self.queens = self.units(UnitTypeId.QUEEN)
        self.zerglings = self.units(UnitTypeId.ZERGLING)

    def hive_units(self):
        """Initialize all our buildings (hive tech)"""
        self.ultralisks = self.units(UnitTypeId.ULTRALISK)

    def lair_units(self):
        """Initialize all our buildings(lair tech)"""
        self.hydras = self.units(UnitTypeId.HYDRALISK)
        self.mutalisks = self.units(UnitTypeId.MUTALISK)
        self.overseers = self.units(UnitTypeId.OVERSEER)
