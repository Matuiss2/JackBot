"""All data that are related to units on our possession are here"""
from sc2.constants import (
    CREEPTUMOR,
    CREEPTUMORBURROWED,
    CREEPTUMORQUEEN,
    DRONE,
    EVOLUTIONCHAMBER,
    EXTRACTOR,
    HATCHERY,
    HIVE,
    HYDRALISK,
    HYDRALISKDEN,
    INFESTATIONPIT,
    LAIR,
    LARVA,
    MUTALISK,
    OVERLORD,
    OVERSEER,
    QUEEN,
    SPAWNINGPOOL,
    SPINECRAWLER,
    SPIRE,
    SPORECRAWLER,
    ULTRALISK,
    ULTRALISKCAVERN,
    ZERGLING,
)


class OurUnitsData:
    """This is the data container for all our units and buildings data"""
    def __init__(self):
        self.hatcheries = self.lairs = self.hives = self.overlords = self.drones = self.queens = self.zerglings = None
        self.ultralisks = self.overseers = self.mutalisks = self.larvae = self.hydras = self.evochambers = None
        self.caverns = self.hydradens = self.pools = self.pits = self.spines = self.tumors = self.extractors = None
        self.spores = self.spires = self.structures = None
        self.burrowed_lings = []

    def initialize_bases(self):
        """Initialize the bases"""
        self.hatcheries = self.units(HATCHERY)
        self.lairs = self.units(LAIR)
        self.hives = self.units(HIVE)

    def initialize_units(self):
        """Initialize our units"""
        self.overlords = self.units(OVERLORD)
        self.drones = self.units(DRONE)
        self.queens = self.units(QUEEN)
        self.zerglings = (
            self.units(ZERGLING).tags_not_in(self.burrowed_lings) if self.burrowed_lings else self.units(ZERGLING)
        )
        self.ultralisks = self.units(ULTRALISK)
        self.overseers = self.units(OVERSEER)
        self.mutalisks = self.units(MUTALISK)
        self.larvae = self.units(LARVA)
        self.hydras = self.units(HYDRALISK)

    def initialize_buildings(self):
        """Initialize our buildings"""
        self.structures = self.units.structure
        self.evochambers = self.units(EVOLUTIONCHAMBER)
        self.caverns = self.units(ULTRALISKCAVERN)
        self.hydradens = self.units(HYDRALISKDEN)
        self.pools = self.units(SPAWNINGPOOL)
        self.pits = self.units(INFESTATIONPIT)
        self.spines = self.units(SPINECRAWLER)
        self.tumors = self.units.of_type({CREEPTUMORQUEEN, CREEPTUMOR, CREEPTUMORBURROWED})
        self.extractors = self.units(EXTRACTOR)
        self.spores = self.units(SPORECRAWLER)
        self.spires = self.units(SPIRE)
