"""SC2 zerg bot by Matuiss with huge help of Thommath, Tweakimp, Burny, Helfull and Niknoc"""
import sys
import sc2
from sc2.constants import UnitTypeId
from sc2.position import Point2
from actions.anti_cheese.defend_proxies import DefendProxies
from actions.anti_cheese.defend_worker_rush import DefendWorkerRush
from actions.macro.build.cavern import BuildCavern
from actions.macro.build.creep_spread import CreepControl
from actions.macro.build.creep_tumor import CreepTumor
from actions.macro.build.evochamber import BuildEvochamber
from actions.macro.build.expansion import BuildExpansion
from actions.macro.build.extractor import BuildExtractor
from actions.macro.build.hive import BuildHive
from actions.macro.build.hydraden import BuildHydraden
from actions.macro.build.lair import BuildLair
from actions.macro.build.pit import BuildPit
from actions.macro.build.pool import BuildPool
from actions.macro.build.spines import BuildSpines
from actions.macro.build.spire import BuildSpire
from actions.macro.build.spores import BuildSpores
from actions.macro.building_positioning import BuildingPositioning
from actions.micro.cancel_building import Buildings
from actions.macro.distribute_workers import DistributeWorkers
from actions.micro.micro_main import ArmyControl
from actions.micro.unit.drone import Drone
from actions.micro.unit.overlord import Overlord
from actions.micro.unit.overseer import Overseer
from actions.micro.unit.queen import QueensAbilities
from actions.macro.train.hydras import TrainHydralisk
from actions.macro.train.mutalisk import TrainMutalisk
from actions.macro.train.overlord import TrainOverlord
from actions.macro.train.overseer import TrainOverseer
from actions.macro.train.queen import TrainQueen
from actions.macro.train.ultralisk import TrainUltralisk
from actions.macro.train.drone import TrainDrone
from actions.macro.train.zergling import TrainZergling
from actions.macro.upgrades.spawning_pool_upgrades import UpgradesFromSpawningPool
from actions.macro.upgrades.evochamber_upgrades import UpgradesFromEvochamber
from actions.macro.upgrades.hydraden_upgrades import UpgradesFromHydraden
from actions.macro.upgrades.cavern_upgrades import UpgradesFromCavern
from data_containers.data_container import MainDataContainer
from global_helpers import Globals


class JackBot(sc2.BotAI, MainDataContainer, CreepControl, BuildingPositioning, Globals):
    """It makes periodic attacks with zerglings early, it goes hydras mid-game and ultras end-game"""

    def __init__(self):
        CreepControl.__init__(self)
        MainDataContainer.__init__(self)
        BuildingPositioning.__init__(self)
        self.iteration = self.add_action = None
        self.unit_commands = (
            DefendWorkerRush(self),
            DefendProxies(self),
            DistributeWorkers(self),
            ArmyControl(self),
            QueensAbilities(self),
            CreepTumor(self),
            Drone(self),
            Overseer(self),
            Overlord(self),
            Buildings(self),
        )
        self.train_commands = (
            TrainOverlord(self),
            TrainDrone(self),
            TrainQueen(self),
            TrainUltralisk(self),
            TrainZergling(self),
            TrainOverseer(self),
            TrainMutalisk(self),
            TrainHydralisk(self),
        )
        self.build_commands = (
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
            BuildHydraden(self),
        )
        self.upgrade_commands = (
            UpgradesFromSpawningPool(self),
            UpgradesFromEvochamber(self),
            UpgradesFromHydraden(self),
            UpgradesFromCavern(self),
        )
        self.ordered_expansions = []

    async def on_building_construction_complete(self, unit):
        """Prepares all the building placements near a new expansion"""
        if unit.type_id == UnitTypeId.HATCHERY:
            await self.prepare_building_positions(unit.position)

    def on_end(self, game_result):
        print(game_result)
        sys.exit()

    async def on_step(self, iteration):
        """Group all other functions in this bot, its the main"""
        if self.iteration == iteration:
            return None
        self.iteration = iteration
        self.prepare_data()
        self.set_game_step()
        actions = []
        self.add_action = actions.append
        if not iteration:
            await self.prepare_building_positions(self.townhalls.first.position)
            await self.prepare_expansions()
            self.split_workers()
        if self.minerals >= 25:
            await self.run_commands(self.train_commands)
        await self.run_commands(self.unit_commands)
        await self.run_commands(self.build_commands)
        await self.run_commands(self.upgrade_commands)
        if actions:
            await self.do_actions(actions)

    async def prepare_expansions(self):
        """Prepare all expansion locations and put it in order based on pathing distance"""
        start = self.start_location
        waypoints = [
            (await self._client.query_pathing(start, point), point)
            for point in list(self.expansion_locations)
            if await self._client.query_pathing(start, point)
        ]  # remove all None values for pathing
        # p1 is the expansion location - p0 is the pathing distance to the starting base
        self.ordered_expansions = [Point2((p[1])) for p in sorted(waypoints, key=lambda p: p[0])]

    @staticmethod
    async def run_commands(commands):
        """Group all requirements and execution for a class logic"""
        for command in commands:
            if await command.should_handle():
                await command.handle()

    def set_game_step(self):
        """It sets the interval of frames that it will take to make the actions, depending of the game situation"""
        if self.ground_enemies:
            if len(self.ground_enemies) >= 30:
                self._client.game_step = 1
            elif len(self.ground_enemies) >= 15:
                self._client.game_step = 2
            elif len(self.ground_enemies) >= 5:
                self._client.game_step = 3
            else:
                self._client.game_step = 4
        else:
            self._client.game_step = 6

    def split_workers(self):
        """Split the workers on the beginning """
        for drone in self.drones:
            self.add_action(drone.gather(self.state.mineral_field.closest_to(drone)))
