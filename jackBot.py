"""SC2 zerg bot by Helfull, Matuiss, Thommath and Tweakimp"""
import sc2
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
    PHOTONCANNON,
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
from sc2.position import Point2

from actions.army_control import ArmyControl
from actions.build.cavern import BuildCavern
from actions.build.evochamber import BuildEvochamber
from actions.build.expansion import BuildExpansion
from actions.build.extractor import BuildExtractor
from actions.build.hive import BuildHive
from actions.build.lair import BuildLair
from actions.build.pit import BuildPit
from actions.build.pool import BuildPool
from actions.build.spines import BuildSpines

from actions.build.spire import BuildSpire
from actions.build.spores import BuildSpores
from actions.defend_worker_rush import DefendWorkerRush
from actions.defend_rush_buildings import DefendRushBuildings
from actions.distribute_workers import DistributeWorkers
from actions.queens_abilities import QueensAbilities

from actions.train.mutalisk import TrainMutalisk
from actions.train.overlord import TrainOverlord
from actions.train.overseer import TrainOverseer
from actions.train.queen import TrainQueen
from actions.train.ultralisk import TrainUltralisk
from actions.train.worker import TrainWorker
from actions.train.zergling import TrainZergling
from actions.unit.creep_tumor import CreepTumor
from actions.unit.drone import Drone
from actions.unit.hatchery import Hatchery
from actions.unit.overlord import Overlord
from actions.unit.overseer import Overseer
from actions.upgrades.adrenalglands import UpgradeAdrenalGlands

# from actions.upgrades.burrow import UpgradeBurrow
from actions.upgrades.chitinous_plating import UpgradeChitinousPlating
from actions.upgrades.evochamber import UpgradeEvochamber
from actions.upgrades.metabolicboost import UpgradeMetabolicBoost
from actions.upgrades.pneumatized_carapace import UpgradePneumatizedCarapace
from actions.building_positioning import building_positioning
from creep_spread import CreepControl


# noinspection PyMissingConstructor
class EarlyAggro(sc2.BotAI, CreepControl, building_positioning):
    """It makes periodic attacks with good surrounding and targeting micro, it goes ultras end-game"""

    def __init__(self, debug=False):
        CreepControl.__init__(self)

        self.debug = debug
        self.unit_commands = [
            DefendWorkerRush(self),
            DefendRushBuildings(self),
            DistributeWorkers(self),
            ArmyControl(self),
            QueensAbilities(self),
            CreepTumor(self),
            Drone(self),
            Overseer(self),
            Overlord(self),
            Hatchery(self),
        ]

        self.train_commands = [
            TrainOverlord(self),
            TrainWorker(self),
            TrainQueen(self),
            TrainUltralisk(self),
            TrainZergling(self),
            TrainOverseer(self),
            TrainMutalisk(self),
        ]

        self.build_commands = [
            BuildPool(self),
            BuildExpansion(self),
            BuildExtractor(self),
            BuildEvochamber(self),
            BuildCavern(self),
            BuildPit(self),
            BuildHive(self),
            BuildLair(self),
            BuildSpines(self),
            BuildSpores(self),
            BuildSpire(self),
        ]

        self.upgrade_commands = [
            UpgradeChitinousPlating(self),
            UpgradeMetabolicBoost(self),
            UpgradeAdrenalGlands(self),
            UpgradeEvochamber(self),
            UpgradePneumatizedCarapace(self),
            # UpgradeBurrow(self),
        ]

        self.actions = []
        self.locations = []
        self.ordered_expansions = []
        self.building_positions = []
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
        self.ground_enemies = None

    def get_units(self):
        self.hatcheries = self.units(HATCHERY)
        self.lairs = self.units(LAIR)
        self.hives = self.units(HIVE)
        self.bases = self.hatcheries | self.lairs | self.hives
        self.overlords = self.units(OVERLORD)
        self.drones = self.units(DRONE)
        self.queens = self.units(QUEEN)
        self.zerglings = self.units(ZERGLING)
        self.ultralisks = self.units(ULTRALISK)
        self.overseers = self.units(OVERSEER)
        self.evochambers = self.units(EVOLUTIONCHAMBER)
        self.caverns = self.units(ULTRALISKCAVERN)
        self.pools = self.units(SPAWNINGPOOL)
        self.pits = self.units(INFESTATIONPIT)
        self.spines = self.units(SPINECRAWLER)
        self.tumors = self.units.of_type([CREEPTUMORQUEEN, CREEPTUMOR, CREEPTUMORBURROWED])
        self.larvae = self.units(LARVA)
        self.extractors = self.units(EXTRACTOR)
        self.pit = self.units(INFESTATIONPIT)
        self.spores = self.units(SPORECRAWLER)
        self.spires = self.units(SPIRE)
        self.mutalisks = self.units(MUTALISK)
        self.ground_enemies = self.known_enemy_units.not_flying.not_structure

    def set_game_step(self):
        if self.ground_enemies:
            if len(self.ground_enemies) > 5:
                self._client.game_step = 2
            else:
                self._client.game_step = 4
        else:
            self._client.game_step = 8

    async def on_unit_created(self, unit):
        if unit.type_id is HATCHERY:
            await self.prepare_building_positions(unit)

    async def on_step(self, iteration):
        """Calls used units here, so it just calls it once per loop"""
        self.get_units()
        self.set_game_step()
        self.close_enemies_to_base = False
        self.close_enemy_production = False

        self.actions = []

        if iteration == 0:
            # self._client.game_step = 4  # actions every 4 frames-(optimizing so we can get it to 1 is ideal)
            self.locations = list(self.expansion_locations.keys())
            # await self.prepare_building_positions(self.units(HATCHERY).first)
            self.prepare_expansions()
            self.split_workers()

        if self.ground_enemies:
            for hatch in self.townhalls:
                close_enemy = self.ground_enemies.closer_than(40, hatch.position)
                enemies = close_enemy.exclude_type({DRONE, SCV, PROBE})
                if enemies:
                    self.close_enemies_to_base = True
                    break

        if self.known_enemy_structures.of_type({BARRACKS, GATEWAY, PHOTONCANNON}).closer_than(50, self.start_location):
            self.close_enemy_production = True

        if (
            self.known_enemy_structures.flying
            and len(self.known_enemy_structures) == len(self.known_enemy_structures.flying)
            and self.time > 300
        ):
            self.floating_buildings_bm = True

        await self.run_commands(self.unit_commands, iteration)
        await self.run_commands(self.train_commands, iteration)
        await self.run_commands(self.build_commands, iteration)
        await self.run_commands(self.upgrade_commands, iteration)

        if self.actions:
            if self.debug:
                print(self.actions)
            await self.do_actions(self.actions)

    async def run_commands(self, commands, iteration):
        for command in commands:
            if await command.should_handle(iteration):
                if self.debug:
                    print(f"Handling: {command.__class__}")
                await command.handle(iteration)

    def can_train(self, unit_type, larva=True):
        return (not larva or self.larvae) and self.can_afford(unit_type) and self.can_feed(unit_type)

    def prepare_expansions(self):
        start = self.start_location
        expansions = self.expansion_locations
        waypoints = [point for point in expansions]
        waypoints.sort(key=lambda p: (p[0] - start[0]) ** 2 + (p[1] - start[1]) ** 2)
        self.ordered_expansions = [Point2((p[0], p[1])) for p in waypoints]

    def split_workers(self):
        """Split the workers on the beginning """
        for drone in self.drones:
            closest_mineral_patch = self.state.mineral_field.closest_to(drone)
            self.actions.append(drone.gather(closest_mineral_patch))
