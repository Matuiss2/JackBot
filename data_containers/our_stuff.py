"""All data that on our possession are here"""
from sc2.constants import HATCHERY, HIVE, LAIR

from data_containers.our_structures import OurBuildingsData
from data_containers.our_units import OurUnitsData


class OurStuffData(OurBuildingsData, OurUnitsData):
    """This is the data container for all our units and buildings data"""

    def __init__(self):
        OurBuildingsData.__init__(self)
        OurUnitsData.__init__(self)
        self.structures = self.hatcheries = self.lairs = self.hives = None

    def initialize_our_stuff(self):
        """Initializes our stuff"""
        self.initialize_units()
        self.initialize_buildings()
        self.initialize_bases()

    def initialize_units(self):
        """Initialize our units"""
        self.initialize_hatchery_units()
        self.initialize_lair_units()
        self.initialize_hive_units()

    def initialize_buildings(self):
        """Initialize all our buildings"""
        self.structures = self.units.structure
        self.initialize_hatchery_buildings()
        self.initialize_lair_buildings()
        self.initialize_hive_buildings()

    def initialize_bases(self):
        """Initialize the bases"""
        self.hatcheries = self.units(HATCHERY)
        self.lairs = self.units(LAIR)
        self.hives = self.units(HIVE)
