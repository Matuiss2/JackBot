"""SC2 zerg bot by Matuiss with help of:
Thommath(made the initial creep spread code),
Tweakimp(made the initial building positioning, anti-drone-rush, worker distribution, among other helps),
Burny(this bot is derived from his CreepyBot, it's already very different but give credit where it's due),
Helfull(the idea and implementation of this bots structure came from him, also made the initial effect dodging code),
Niknoc(made the initial hydra micro code) ,
Turing's Ego(helped with the code cleaning)"""
import sc2
from sc2.constants import UnitTypeId, UpgradeId
from sc2.position import Point2
from actions import get_unit_commands
from actions.macro.build import get_build_commands
from actions.macro.build.creep_spread import CreepSpread
from actions.macro.train import get_train_commands
from actions.macro.buildings_positions import BuildingsPositions
from actions.macro.upgrades import get_upgrade_commands
from data_containers.data_container import MainDataContainer
from global_helpers import Globals


class JackBot(sc2.BotAI, MainDataContainer, CreepSpread, BuildingsPositions, Globals):
    """It makes periodic attacks with zerglings early, it goes hydras mid-game and ultras end-game"""

    def __init__(self):
        CreepSpread.__init__(self)
        MainDataContainer.__init__(self)
        BuildingsPositions.__init__(self)
        self.iteration = self.add_action = self.hydra_range = self.hydra_speed = self.zergling_atk_spd = None
        self.unit_commands = get_unit_commands(self)
        self.train_commands = get_train_commands(self)
        self.build_commands = get_build_commands(self)
        self.upgrade_commands = get_upgrade_commands(self)
        self.ordered_expansions, self.finished_upgrades = [], []

    def already_pending_upgrade(self, upg):
        """todo: remove when bug is fixed"""
        pending = super().already_pending_upgrade(upg)
        if 0 < pending < 0.99:
            return pending
        if pending >= 0.99:
            self.finished_upgrades.append(upg)
        if upg in self.finished_upgrades:
            return 1
        return 0

    async def on_building_construction_complete(self, unit):
        """Prepares all the building placements near a new expansion"""
        if unit.type_id == UnitTypeId.HATCHERY:
            await self.prepare_building_positions(unit.position)

    async def on_upgrade_complete(self, upgrade):
        if upgrade == UpgradeId.EVOLVEGROOVEDSPINES:
            self.hydra_range = True
        elif upgrade == UpgradeId.EVOLVEMUSCULARAUGMENTS:
            self.hydra_speed = True
        elif upgrade == UpgradeId.ZERGLINGATTACKSPEED:
            self.zergling_atk_spd = True

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
        if self.minerals >= 50:
            await self.run_commands(self.train_commands)
        await self.run_commands(self.unit_commands)
        await self.run_commands(self.build_commands)
        if self.minerals >= 100 and self.vespene >= 100:
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
        self.ordered_expansions = [start] + [Point2((p[1])) for p in sorted(waypoints, key=lambda p: p[0])]

    @staticmethod
    async def run_commands(commands):
        """Group all requirements and execution for a class logic"""
        for command in commands:
            if await command.should_handle():
                await command.handle()

    def set_game_step(self):
        """It sets the interval of frames that it will take to make the actions, depending of the game situation"""
        if self.ground_enemies:
            if len(self.ground_enemies) >= 15:
                self._client.game_step = 1
            else:
                self._client.game_step = 2
        else:
            self._client.game_step = 3

    def split_workers(self):
        """Split the workers on the beginning """
        for drone in self.drones:
            self.add_action(drone.gather(self.state.mineral_field.closest_to(drone)))
