from sc2.constants import (
    BARRACKS,
    CREEPTUMOR,
    CREEPTUMORBURROWED,
    CREEPTUMORQUEEN,
    DRONE,
    EVOLUTIONCHAMBER,
    EXTRACTOR,
    GATEWAY,
    HATCHERY,
    HIVE,
    INFESTATIONPIT,
    LAIR,
    LARVA,
    MUTALISK,
    OVERLORD,
    OVERSEER,
    PROBE,
    QUEEN,
    SCV,
    SPAWNINGPOOL,
    SPINECRAWLER,
    SPIRE,
    SPORECRAWLER,
    ULTRALISK,
    ULTRALISKCAVERN,
    ZERGLING,
)

class DataContainer:

    def __init__(self):
        self.close_enemies_to_base = False
        self.close_enemy_production = False
        self.floating_buildings_bm = False
        self.hatcheries = None
        self.lairs = None
        self.hives = None
        self.bases = None
        self.overlords = None
        self.drones = None
        self.queens = None
        self.zerglings = None
        self.burrowed_lings = []
        self.ultralisks = None
        self.overseers = None
        self.evochambers = None
        self.caverns = None
        self.pools = None
        self.pits = None
        self.spines = None
        self.tumors = None
        self.larvae = None
        self.extractors = None
        self.mutalisks = None
        self.pit = None
        self.spores = None
        self.spires = None
        self.structures = None
        self.enemies = None
        self.enemy_structures = None
        self.ground_enemies = None
        self.furthes_townhall_to_map_center = None

    def prepare_data(self):
        """Prepares the data"""
        self.hatcheries = self.units(HATCHERY)
        self.lairs = self.units(LAIR)
        self.hives = self.units(HIVE)
        self.bases = self.hatcheries | self.lairs | self.hives
        self.overlords = self.units(OVERLORD)
        self.drones = self.units(DRONE)
        self.queens = self.units(QUEEN)
        self.zerglings = (
            self.units(ZERGLING).tags_not_in(self.burrowed_lings) if self.burrowed_lings else self.units(ZERGLING)
        )
        self.ultralisks = self.units(ULTRALISK)
        self.overseers = self.units(OVERSEER)
        self.evochambers = self.units(EVOLUTIONCHAMBER)
        self.caverns = self.units(ULTRALISKCAVERN)
        self.pools = self.units(SPAWNINGPOOL)
        self.pits = self.units(INFESTATIONPIT)
        self.spines = self.units(SPINECRAWLER)
        self.tumors = self.units.of_type({CREEPTUMORQUEEN, CREEPTUMOR, CREEPTUMORBURROWED})
        self.larvae = self.units(LARVA)
        self.extractors = self.units(EXTRACTOR)
        self.pit = self.units(INFESTATIONPIT)
        self.spores = self.units(SPORECRAWLER)
        self.spires = self.units(SPIRE)
        self.mutalisks = self.units(MUTALISK)
        self.enemies = self.known_enemy_units
        self.enemy_structures = self.known_enemy_structures
        self.ground_enemies = self.known_enemy_units.not_flying.not_structure
        if self.townhalls:
            self.furthes_townhall_to_map_center = self.townhalls.furthest_to(self.game_info.map_center)
        self.structures = self.units.structure

        if self.ground_enemies:
            for hatch in self.townhalls:
                close_enemy = self.ground_enemies.closer_than(40, hatch.position)
                enemies = close_enemy.exclude_type({DRONE, SCV, PROBE})
                if enemies:
                    self.close_enemies_to_base = True
                    break

        if self.known_enemy_structures.of_type({BARRACKS, GATEWAY}).closer_than(75, self.start_location):
            self.close_enemy_production = True

        if (
            self.known_enemy_structures.flying
            and len(self.known_enemy_structures) == len(self.known_enemy_structures.flying)
            and self.time > 300
        ):
            self.floating_buildings_bm = True
