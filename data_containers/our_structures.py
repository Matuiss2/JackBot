"""All data that are related to structures on our possession are here"""
from sc2.constants import (
    CREEPTUMOR,
    CREEPTUMORBURROWED,
    CREEPTUMORQUEEN,
    EVOLUTIONCHAMBER,
    EXTRACTOR,
    HYDRALISKDEN,
    INFESTATIONPIT,
    SPAWNINGPOOL,
    SPINECRAWLER,
    SPIRE,
    SPORECRAWLER,
    ULTRALISKCAVERN,
)


class OurBuildingsData:
    """This is the data container for all our buildings data"""

    def __init__(self):
        self.evochambers = self.pools = self.spines = self.tumors = self.extractors = self.spores = self.spires = None
        self.hydradens = self.pits = self.caverns = None

    def initialize_hatchery_buildings(self):
        """Initialize all our buildings(hatchery tech)"""
        self.evochambers = self.units(EVOLUTIONCHAMBER)
        self.pools = self.units(SPAWNINGPOOL)
        self.spines = self.units(SPINECRAWLER)
        self.tumors = self.units.of_type({CREEPTUMORQUEEN, CREEPTUMOR, CREEPTUMORBURROWED})
        self.extractors = self.units(EXTRACTOR)
        self.spores = self.units(SPORECRAWLER)
        self.spires = self.units(SPIRE)

    def initialize_lair_buildings(self):
        """Initialize all our buildings(lair tech)"""
        self.hydradens = self.units(HYDRALISKDEN)
        self.pits = self.units(INFESTATIONPIT)

    def initialize_hive_buildings(self):
        """Initialize all our buildings (hive tech)"""
        self.caverns = self.units(ULTRALISKCAVERN)
