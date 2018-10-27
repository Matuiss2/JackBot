from sc2.constants import UnitTypeId

class DataContainer:

    def __init__(self):
        self.close_enemies_to_base = False
        self.close_enemy_production = False
        self.counter_attack_vs_flying = False
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
        self.furthest_townhall_to_map_center = None

    def prepare_data(self):
        """Prepares the data"""
        self.close_enemies_to_base = False
        self.close_enemy_production = False
        self.counter_attack_vs_flying = False

        # prepare units
        self.structures = self.units.structure

        # Prepare bases
        self.hatcheries = self.units(UnitTypeId.HATCHERY)
        self.lairs = self.units(UnitTypeId.LAIR)
        self.hives = self.units(UnitTypeId.HIVE)
        self.bases = self.hatcheries | self.lairs | self.hives
        if self.bases:
            self.furthest_townhall_to_map_center = self.bases.furthest_to(self.game_info.map_center)

        # prepare own units
        self.overlords = self.units(UnitTypeId.OVERLORD)
        self.drones = self.units(UnitTypeId.DRONE)
        self.queens = self.units(UnitTypeId.QUEEN)
        self.zerglings = (
            self.units(UnitTypeId.ZERGLING).tags_not_in(self.burrowed_lings) if self.burrowed_lings else self.units(UnitTypeId.ZERGLING)
        )
        self.ultralisks = self.units(UnitTypeId.ULTRALISK)
        self.overseers = self.units(UnitTypeId.OVERSEER)
        self.evochambers = self.units(UnitTypeId.EVOLUTIONCHAMBER)
        self.caverns = self.units(UnitTypeId.ULTRALISKCAVERN)
        self.pools = self.units(UnitTypeId.SPAWNINGPOOL)
        self.pits = self.units(UnitTypeId.INFESTATIONPIT)
        self.spines = self.units(UnitTypeId.SPINECRAWLER)
        self.tumors = self.units.of_type({UnitTypeId.CREEPTUMORQUEEN, UnitTypeId.CREEPTUMOR, UnitTypeId.CREEPTUMORBURROWED})
        self.larvae = self.units(UnitTypeId.LARVA)
        self.extractors = self.units(UnitTypeId.EXTRACTOR)
        self.pit = self.units(UnitTypeId.INFESTATIONPIT)
        self.spores = self.units(UnitTypeId.SPORECRAWLER)
        self.spires = self.units(UnitTypeId.SPIRE)
        self.mutalisks = self.units(UnitTypeId.MUTALISK)

        # prepare enemy units
        self.enemies = self.known_enemy_units
        self.flying_enemies = self.enemies.flying
        self.ground_enemies = self.enemies.not_flying.not_structure
        self.enemy_structures = self.known_enemy_structures

        if self.enemies:
            excluded_from_flying = {
                UnitTypeId.DRONE,
                UnitTypeId.SCV,
                UnitTypeId.PROBE,
                UnitTypeId.OVERLORD,
                UnitTypeId.OVERSEER,
                UnitTypeId.RAVEN,
                UnitTypeId.OBSERVER,
                UnitTypeId.WARPPRISM,
                UnitTypeId.MEDIVAC,
                UnitTypeId.VIPER,
                UnitTypeId.CORRUPTOR
            }
            for hatch in self.bases:
                close_enemy = self.ground_enemies.closer_than(25, hatch.position)
                close_enemy_flying = self.flying_enemies.closer_than(30, hatch.position)
                enemies = close_enemy.exclude_type({UnitTypeId.DRONE, UnitTypeId.SCV, UnitTypeId.PROBE})
                enemies_flying = close_enemy_flying.exclude_type(excluded_from_flying)
                if enemies_flying and not self.counter_attack_vs_flying:
                    self.counter_attack_vs_flying = True
                if enemies and not self.close_enemies_to_base:
                    self.close_enemies_to_base = True

        self.check_for_proxy_buildings()
        self.check_for_floating_buildings()

    def check_for_proxy_buildings(self):
        """Check if there are any proxy buildings"""
        if (
            self.enemy_structures
                .of_type({UnitTypeId.BARRACKS, UnitTypeId.GATEWAY})
                .closer_than(75, self.start_location)
        ):
            self.close_enemy_production = True

    def check_for_floating_buildings(self):
        """Check if some terran wants to be funny with lifting up"""
        if (
            self.enemy_structures.flying
            and len(self.enemy_structures) == len(self.enemy_structures.flying)
            and self.time > 300
        ):
            self.floating_buildings_bm = True

