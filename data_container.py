"""All global variables and triggers are grouped here"""
from sc2.constants import (
    HATCHERY,
    LAIR,
    HIVE,
    HYDRALISKDEN,
    OVERLORD,
    DRONE,
    QUEEN,
    ZERGLING,
    ULTRALISK,
    OVERSEER,
    EVOLUTIONCHAMBER,
    ULTRALISKCAVERN,
    SPAWNINGPOOL,
    INFESTATIONPIT,
    SPINECRAWLER,
    CREEPTUMORQUEEN,
    CREEPTUMOR,
    CREEPTUMORBURROWED,
    LARVA,
    EXTRACTOR,
    SPORECRAWLER,
    SPIRE,
    MUTALISK,
    BARRACKS,
    GATEWAY,
    SCV,
    PROBE,
    RAVEN,
    OBSERVER,
    WARPPRISM,
    MEDIVAC,
    VIPER,
    CORRUPTOR,
    HYDRALISK,
    COMMANDCENTER,
    NEXUS,
)


class DataContainer:
    """This is the main data container for all data the bot requires"""

    def __init__(self):
        self.close_enemies_to_base = False
        self.close_enemy_production = False
        self.counter_attack_vs_flying = False
        self.floating_buildings_bm = False
        self.one_base_play = False
        self.hatcheries = None
        self.lairs = None
        self.hives = None
        self.hydras = None
        self.overlords = None
        self.drones = None
        self.queens = None
        self.zerglings = None
        self.burrowed_lings = []
        self.ultralisks = None
        self.overseers = None
        self.evochambers = None
        self.caverns = None
        self.hydradens = None
        self.pools = None
        self.pits = None
        self.spines = None
        self.tumors = None
        self.larvae = None
        self.extractors = None
        self.mutalisks = None
        self.spores = None
        self.spires = None
        self.structures = None
        self.enemies = None
        self.enemy_structures = None
        self.flying_enemies = None
        self.ground_enemies = None
        self.furthest_townhall_to_map_center = None

    def prepare_data(self):
        """Prepares the data"""
        self.counter_attack_vs_flying = False
        self.close_enemies_to_base = False
        # prepare units
        self.structures = self.units.structure
        self.initialize_bases()
        self.initialize_units()
        self.initialize_buildings()
        self.initialize_enemies()
        self.close_enemy_production = self.check_for_proxy_buildings()
        self.floating_buildings_bm = self.check_for_floating_buildings()
        self.one_base_play = self.check_for_second_bases()

    def check_for_proxy_buildings(self) -> bool:
        """Check if there are any proxy buildings"""
        return bool(self.enemy_structures.of_type({BARRACKS, GATEWAY, HATCHERY}).closer_than(75, self.start_location))

    def check_for_floating_buildings(self) -> bool:
        """Check if some terran wants to be funny with lifting up"""
        return bool(
            self.enemy_structures.flying
            and len(self.enemy_structures) == len(self.enemy_structures.flying)
            and self.time > 300
        )

    def check_for_second_bases(self) -> bool:
        """Check if its a one base play"""
        return bool(
            self.overlords
            and not self.enemy_structures.of_type({NEXUS, COMMANDCENTER, HATCHERY}).closer_than(
                25, self.overlords.furthest_to(self.start_location)
            )
            and self.time > 165
            and not self.close_enemy_production
        )

    def prepare_enemy_data_points(self):
        """Prepare data related to enemy units"""
        if self.enemies:
            excluded_from_flying = {
                DRONE,
                SCV,
                PROBE,
                OVERLORD,
                OVERSEER,
                RAVEN,
                OBSERVER,
                WARPPRISM,
                MEDIVAC,
                VIPER,
                CORRUPTOR,
            }
            for hatch in self.townhalls:
                close_enemy = self.ground_enemies.closer_than(20, hatch.position)
                close_enemy_flying = self.flying_enemies.exclude_type(excluded_from_flying).closer_than(
                    30, hatch.position
                )
                if close_enemy and not self.close_enemies_to_base:
                    self.close_enemies_to_base = True
                if close_enemy_flying and not self.counter_attack_vs_flying:
                    self.counter_attack_vs_flying = True

    def initialize_bases(self):
        """Initialize the bases"""
        self.hatcheries = self.units(HATCHERY)
        self.lairs = self.units(LAIR)
        self.hives = self.units(HIVE)
        self.prepare_bases_data()

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

    def initialize_enemies(self):
        """Initialize everything related to enemies"""
        excluded_from_ground = {DRONE, SCV, PROBE}
        self.enemies = self.known_enemy_units
        self.flying_enemies = self.enemies.flying
        self.ground_enemies = self.enemies.not_flying.not_structure.exclude_type(excluded_from_ground)
        self.enemy_structures = self.known_enemy_structures
        self.prepare_enemy_data_points()

    def prepare_bases_data(self):
        """Prepare data related to our bases"""
        if self.townhalls:
            self.furthest_townhall_to_map_center = self.townhalls.furthest_to(self.game_info.map_center)
