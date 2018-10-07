"""SC2 zerg bot by Helfull, Matuiss, Thommath and Tweakimp"""
import sc2
from sc2.position import Point2
from sc2.constants import (
    HATCHERY, LAIR, HIVE, OVERLORD,
    DRONE, QUEEN, ZERGLING,
    ULTRALISK, OVERSEER, EVOLUTIONCHAMBER,
    ULTRALISKCAVERN, SPAWNINGPOOL, INFESTATIONPIT, SPINECRAWLER,
    BARRACKS, GATEWAY, PHOTONCANNON, SCV, PROBE,
    CREEPTUMORQUEEN, CREEPTUMOR, CREEPTUMORBURROWED,
    LARVA, EXTRACTOR, SPORECRAWLER, MUTALISK
)

from creep_spread import CreepControl

from actions.train.worker import TrainWorker
from actions.train.queen import TrainQueen
from actions.train.overlord import TrainOverlord
from actions.train.zergling import TrainZergling
from actions.train.ultralisk import TrainUltralisk
from actions.train.overseer import TrainOverseer
from actions.train.mutalisk import TrainMutalisk

from actions.build.pool import BuildPool
from actions.build.expansion import BuildExpansion
from actions.build.extractor import BuildExtractor
from actions.build.evochamber import BuildEvochamber
from actions.build.cavern import BuildCavern
from actions.build.pit import BuildPit
from actions.build.lair import BuildLair
from actions.build.hive import BuildHive
from actions.build.spines import BuildSpines
from actions.build.spores import BuildSporse
from actions.build.spire import BuildSpire

from actions.upgrades.metabolicboost import UpgradeMetabolicBoost
from actions.upgrades.adrenalglands import UpgradeAdrenalGlands
from actions.upgrades.evochamber import UpgradeEvochamber
from actions.upgrades.chitinous_plating import UpgradeChitinousPlating
from actions.upgrades.pneumatized_carapace import UpgradePneumatizedCarapace

from actions.unit.creep_tumor import CreepTumor
from actions.unit.drone import Drone
from actions.unit.overseer import Overseer

from actions.distribute_workers import DistributeWorkers
from actions.defend_worker_rush import DefendWorkerRush
from actions.army_control import ArmyControl
from actions.queens_abilities import QueensAbilities


# noinspection PyMissingConstructor
class EarlyAggro(sc2.BotAI, CreepControl):
    """It makes periodic attacks with good surrounding and targeting micro, it goes ultras end-game"""
    def __init__(self, debug=False):
        CreepControl.__init__(self)

        self.debug = debug
        self.unit_commands = [
            DefendWorkerRush(self),
            DistributeWorkers(self),
            ArmyControl(self),
            QueensAbilities(self),
            CreepTumor(self),
            Drone(self),
            Overseer(self)
        ]

        self.train_commands = [
            TrainOverlord(self),
            TrainWorker(self),
            TrainQueen(self),
            TrainUltralisk(self),
            TrainZergling(self),
            TrainOverseer(self),
            TrainMutalisk(self)
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
            BuildSporse(self),
            BuildSpire(self),
        ]

        self.upgrade_commands = [
            UpgradeChitinousPlating(self),
            UpgradeMetabolicBoost(self),
            UpgradeAdrenalGlands(self),
            UpgradeEvochamber(self),
            UpgradePneumatizedCarapace(self),
        ]

        self.pools = []
        self.actions = []
        self.locations = []
        self.ordered_expansions = []
        self.close_enemies_to_base = False
        self.close_enemy_production = False
        self.floating_buildings_bm = False
        self.hatcheries = None
        self.lairs = None
        self.hives = None
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
        self.pit = None
        self.spores = None
        self.mutalisks = None

    def get_units(self):
        self.hatcheries = self.units(HATCHERY)
        self.lairs = self.units(LAIR)
        self.hives = self.units(HIVE)
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
        self.tumors = self.units().of_type([CREEPTUMORQUEEN, CREEPTUMOR, CREEPTUMORBURROWED])
        self.larvae = self.units(LARVA)
        self.extractors = self.units(EXTRACTOR)
        self.pit = self.units(INFESTATIONPIT)
        self.spores = self.units(SPORECRAWLER)
        self.mutalisks = self.units(MUTALISK)

    async def on_step(self, iteration):
        """Calls used units here, so it just calls it once per loop"""
        self.get_units()

        self.close_enemies_to_base = False
        self.close_enemy_production = False
        self.floating_buildings_bm = False

        self.actions = []

        if iteration == 0:
            self._client.game_step = 4  # actions every 4 frames-(optimizing so we can get it to 1 is ideal)
            self.locations = list(self.expansion_locations.keys())
            self.prepare_expansions()
            self.split_workers()

        if self.known_enemy_units.not_structure.not_flying:
            for hatch in self.townhalls:
                close_enemy = self.known_enemy_units.not_structure.not_flying.closer_than(40, hatch.position)
                enemies = close_enemy.exclude_type({DRONE, SCV, PROBE})
                if enemies:
                    self.close_enemies_to_base = True
                    break

        if self.known_enemy_structures.of_type({BARRACKS, GATEWAY, PHOTONCANNON}).closer_than(50, self.start_location):
            self.close_enemy_production = True

        if len(self.known_enemy_structures) == len(self.known_enemy_structures.flying) and self.time > 300:
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
                    print("Handling: {}".format(command.__class__))
                await command.handle(iteration)

    def can_train(self, unit_type, larva=True):
        return (
            (not larva or self.larvae)
            and self.can_afford(unit_type)
            and self.can_feed(unit_type)
        )

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
