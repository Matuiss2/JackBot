"""All data that are related to units on our possession are here"""
from sc2.constants import UnitTypeId


class OurUnitsData:
    """This is the data container for all our units"""

    def __init__(self):
        self.overlords = self.drones = self.queens = self.zerglings = self.larvae = self.overseers = None
        self.mutalisks = self.hydras = self.ultralisks = self.changelings = None
        self.changeling_types = {
            UnitTypeId.CHANGELING,
            UnitTypeId.CHANGELINGZEALOT,
            UnitTypeId.CHANGELINGMARINESHIELD,
            UnitTypeId.CHANGELINGMARINE,
            UnitTypeId.CHANGELINGZERGLINGWINGS,
            UnitTypeId.CHANGELINGZERGLING,
        }

    def hatchery_units(self):
        """Initialize all our buildings(hatchery tech)"""
        self.overlords = self.units(UnitTypeId.OVERLORD)
        self.drones = self.units(UnitTypeId.DRONE)
        self.changelings = self.units.of_type(self.changeling_types)
        self.queens = self.units(UnitTypeId.QUEEN)
        self.zerglings = self.units(UnitTypeId.ZERGLING)
        self.larvae = self.units(UnitTypeId.LARVA)

    def hive_units(self):
        """Initialize all our buildings (hive tech)"""
        self.ultralisks = self.units(UnitTypeId.ULTRALISK)

    def lair_units(self):
        """Initialize all our buildings(lair tech)"""
        self.overseers = self.units(UnitTypeId.OVERSEER)
        self.mutalisks = self.units(UnitTypeId.MUTALISK)
        self.hydras = self.units(UnitTypeId.HYDRALISK)
