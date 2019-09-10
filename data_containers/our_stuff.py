"""All data that are on our possession are here"""
from sc2.constants import UnitTypeId
from data_containers.our_structures import OurBuildingsData
from data_containers.our_units import OurUnitsData
from data_containers.quantity_data import OurQuantityData


class OurStuffData(OurBuildingsData, OurUnitsData, OurQuantityData):
    """This is the data container for all our units and buildings"""

    def __init__(self):
        OurBuildingsData.__init__(self)
        OurUnitsData.__init__(self)
        self.structures = self.hatcheries = self.lairs = self.hives = self.ready_bases = self.upgraded_base = None

    def initialize_our_amounts(self):
        """Initialize the amount of everything(repeated) on our possession"""
        self.buildings_amounts()
        self.unit_amounts()
        self.completed_asset_amounts()
        self.incomplete_asset_amounts()

    def initialize_bases(self):
        """Initialize our bases"""
        self.hatcheries = self.units(UnitTypeId.HATCHERY)
        self.lairs = self.units(UnitTypeId.LAIR)
        self.hives = self.units(UnitTypeId.HIVE)
        self.upgraded_base = self.lairs or self.hives
        self.ready_bases = self.townhalls.ready

    def initialize_buildings(self):
        """Initialize all our buildings"""
        self.structures = self.units.structure
        self.hatchery_buildings()
        self.lair_buildings()
        self.hive_buildings()
        self.finished_buildings()

    def initialize_our_stuff(self):
        """Initializes our stuff"""
        self.initialize_units()
        self.initialize_buildings()
        self.initialize_bases()
        self.initialize_our_amounts()

    def initialize_units(self):
        """Initialize our units"""
        self.hatchery_units()
        self.lair_units()
        self.hive_units()
