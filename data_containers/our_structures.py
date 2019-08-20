"""All data that are related to structures on our possession are here"""
from sc2.constants import UnitTypeId


class OurBuildingsData:
    """This is the data container for all our buildings"""

    def __init__(self):
        self.evochambers = self.pools = self.spines = self.tumors = self.extractors = self.spores = self.spires = None
        self.hydradens = self.pits = self.caverns = self.settled_evochambers = self.settled_pool = None
        self.settled_cavern = self.settled_hydraden = None
        self.creep_types = {UnitTypeId.CREEPTUMORQUEEN, UnitTypeId.CREEPTUMOR, UnitTypeId.CREEPTUMORBURROWED}

    def initialize_hatchery_buildings(self):
        """Initialize all our buildings(hatchery tech)"""
        self.evochambers = self.units(UnitTypeId.EVOLUTIONCHAMBER)
        self.pools = self.units(UnitTypeId.SPAWNINGPOOL)
        self.spines = self.units(UnitTypeId.SPINECRAWLER)
        self.tumors = self.units.of_type(self.creep_types)
        self.extractors = self.units(UnitTypeId.EXTRACTOR)
        self.spores = self.units(UnitTypeId.SPORECRAWLER)
        self.spires = self.units(UnitTypeId.SPIRE)

    def initialize_hive_buildings(self):
        """Initialize all our buildings (hive tech)"""
        self.caverns = self.units(UnitTypeId.ULTRALISKCAVERN)

    def initialize_lair_buildings(self):
        """Initialize all our buildings(lair tech)"""
        self.hydradens = self.units(UnitTypeId.HYDRALISKDEN)
        self.pits = self.units(UnitTypeId.INFESTATIONPIT)

    def initialize_finished_buildings(self):
        self.settled_evochambers = self.evochambers.ready
        self.settled_pool = self.pools.ready
        self.settled_cavern = self.caverns.ready
        self.settled_hydraden = self.hydradens.ready
