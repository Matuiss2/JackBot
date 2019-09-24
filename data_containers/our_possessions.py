"""All data that are on our possession are here"""
from sc2.constants import UnitTypeId
from data_containers.our_structures import OurBuildingsData
from data_containers.our_units import OurUnitsData
from data_containers.quantity_data import OurQuantityData


class OurPossessionsData(OurBuildingsData, OurUnitsData, OurQuantityData):
    """This is the data container for all our units and buildings"""

    def __init__(self):
        OurBuildingsData.__init__(self)
        OurUnitsData.__init__(self)
        self.hatcheries = self.hives = self.lairs = self.ready_bases = self.structures = self.upgraded_base = None

    def initialize_bases(self):
        """Initialize our bases"""
        self.hatcheries = self.units(UnitTypeId.HATCHERY)
        self.hives = self.units(UnitTypeId.HIVE)
        self.lairs = self.units(UnitTypeId.LAIR)
        self.ready_bases = self.townhalls.ready
        self.upgraded_base = self.lairs or self.hives

    def initialize_buildings(self):
        """Initialize all our buildings"""
        self.hatchery_buildings()
        self.hive_buildings()
        self.lair_buildings()
        self.finished_buildings()
        self.structures = self.units.structure

    def initialize_our_amounts(self):
        """Initialize the amount of everything(repeated) on our possession"""
        self.buildings_amounts()
        self.completed_asset_amounts()
        self.incomplete_asset_amounts()
        self.unit_amounts()

    def initialize_our_stuff(self):
        """Initializes our stuff"""
        self.initialize_bases()
        self.initialize_buildings()
        self.initialize_units()
        self.initialize_our_amounts()  # need to come last on the function

    def initialize_units(self):
        """Initialize our units"""
        self.hatchery_units()
        self.hive_units()
        self.lair_units()
