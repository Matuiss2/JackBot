"""Global methods and class for the bot go here"""
import math
import random
import logging
from typing import List, Dict, Optional, Union
import statistics
from .position import Point2, Point3
from .data import Race, ActionResult, race_worker, race_townhalls, race_gas, Target, Result
from .unit import Unit
from .cache import property_cache_forever
from .game_data import AbilityData
from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId
from .ids.upgrade_id import UpgradeId
from .units import Units


from .game_state import GameState
from .game_data import GameData

LOGGER = logging.getLogger(__name__)


class BotAI:
    """Base class for bots."""

    EXPANSION_GAP_THRESHOLD = 15

    def __init__(self):
        self.enemy_id = None
        self.units = None
        self.workers = None
        self.townhalls = None
        self.geysers = None
        self.minerals = None
        self.vespene = None
        self.supply_used = None
        self.supply_cap = None
        self.supply_left = None
        self._client = None
        self._game_info = None
        self._game_data = None
        self.player_id = None
        self.race = None
        self._units_previous_map = None
        self.units = None
        self.state = None

    @property
    def enemy_race(self) -> Race:
        """Returns the enemy race"""
        self.enemy_id = 3 - self.player_id
        return Race(self._game_info.player_races[self.enemy_id])

    @property
    def time(self) -> Union[int, float]:
        """Returns time in seconds, assumes the game is played on 'faster' """
        return self.state.game_loop / 22.4  # / (1/1.4) * (1/16)

    @property
    def game_info(self) -> "GameInfo":
        """Getter for _game_info"""
        return self._game_info

    @property
    def game_data(self) -> GameData:
        """Getter for _game_data"""
        return self._game_data

    @property
    def client(self) -> "Client":
        """Getter for _client"""
        return self._client

    @property
    def start_location(self) -> Point2:
        """Position of the starting base"""
        return self._game_info.player_start_location

    @property
    def enemy_start_locations(self) -> List[Point2]:
        """Possible start locations for enemies."""
        return self._game_info.start_locations

    @property
    def known_enemy_units(self) -> Units:
        """List of known enemy units, including structures."""
        return self.state.units.enemy

    @property
    def known_enemy_structures(self) -> Units:
        """List of known enemy units, structures only."""
        return self.state.units.enemy.structure

    @property
    def main_base_ramp(self) -> "Ramp":
        """ Returns the Ramp instance of the closest main-ramp to start location.
         Look in game_info.py for more information """
        if hasattr(self, "cached_main_base_ramp"):
            return self.cached_main_base_ramp
        return min(
            {ramp for ramp in self.game_info.map_ramps if len(ramp.upper2_for_ramp_wall) == 2},
            key=(lambda r: self.start_location.distance_to(r.top_center)),
        )

    @property_cache_forever
    def expansion_locations(self) -> Dict[Point2, Units]:
        """List of possible expansion locations."""
        resource_spread_threshhold = 100
        resources = self.state.mineral_field | self.state.vespene_geyser
        r_groups = []
        for mineral_field in resources:
            for group in r_groups:
                if any(
                    self.get_terrain_height(mineral_field.position) == self.get_terrain_height(p.position)
                    and mineral_field.position.distance_squared(p.position) < resource_spread_threshhold
                    for p in group
                ):
                    group.append(mineral_field)
                    break
            else:
                r_groups.append([mineral_field])
        r_groups = [g for g in r_groups if len(g) > 1]
        offsets = [(x, y) for x in range(-9, 10) for y in range(-9, 10) if 75 >= x ** 2 + y ** 2 >= 49]
        centers = {}
        for resources in r_groups:
            possible_points = [
                Point2((offset[0] + resources[-1].position.x, offset[1] + resources[-1].position.y))
                for offset in offsets
            ]
            possible_points.sort(
                key=lambda p: statistics.mean([abs(p.distance_to(resource) - 7.162) for resource in resources])
            )
            centers[possible_points[0]] = resources
        return centers

    async def get_available_abilities(
        self, units: Union[List[Unit], Units], ignore_resource_requirements=False
    ) -> List[List[AbilityId]]:
        """ Returns available abilities of one or more units. """
        return await self._client.query_available_abilities(units, ignore_resource_requirements)

    async def expand_now(
        self, building: UnitTypeId = None, max_distance: Union[int, float] = 10, location: Optional[Point2] = None
    ):
        """Takes new expansion."""
        if not building:
            start_townhall_type = {
                Race.Protoss: UnitTypeId.NEXUS,
                Race.Terran: UnitTypeId.COMMANDCENTER,
                Race.Zerg: UnitTypeId.HATCHERY,
            }
            building = start_townhall_type[self.race]
        assert isinstance(building, UnitTypeId)
        if not location:
            location = await self.get_next_expansion()
        await self.build(building, near=location, max_distance=max_distance, random_alternative=False, placement_step=1)

    def is_near_to_expansion(self, unit, exp_loc):
        """If the expansion location is already taken returns True"""
        return unit.position.distance_to(exp_loc) < self.EXPANSION_GAP_THRESHOLD

    async def get_next_expansion(self) -> Optional[Point2]:
        """Find next expansion location. Changed by Matuiss recently, untested"""
        closest = None
        distance = math.inf
        for exp_loc in self.expansion_locations:
            if any(self.is_near_to_expansion(th, exp_loc) for th in self.townhalls):
                continue
            startp = self._game_info.player_start_location
            pathing_distance = await self._client.query_pathing(startp, exp_loc)
            if pathing_distance is None:
                continue
            if pathing_distance < distance:
                distance = pathing_distance
                closest = exp_loc
        return closest

    async def distribute_workers(self):
        """
        Distributes workers across all the bases taken.
        WARNING: This is quite slow when there are lots of workers or multiple bases.
        """
        owned_expansions = self.owned_expansions
        worker_pool = []
        actions = []
        for idle_worker in self.workers.idle:
            mineral_field = self.state.mineral_field.closest_to(idle_worker)
            actions.append(idle_worker.gather(mineral_field))
        for location, townhall in owned_expansions.items():
            workers = self.workers.closer_than(20, location)
            actual = townhall.assigned_harvesters
            ideal = townhall.ideal_harvesters
            excess = actual - ideal
            if actual > ideal:
                worker_pool.extend(workers.random_group_of(min(excess, len(workers))))
                continue
        for geyser in self.geysers:
            workers = self.workers.closer_than(5, geyser)
            actual = geyser.assigned_harvesters
            ideal = geyser.ideal_harvesters
            excess = actual - ideal
            if actual > ideal:
                worker_pool.extend(workers.random_group_of(min(excess, len(workers))))
                continue
        for geyser in self.geysers:
            actual = geyser.assigned_harvesters
            ideal = geyser.ideal_harvesters
            deficit = ideal - actual

            for _ in range(0, deficit):
                if worker_pool:
                    selected_worker = worker_pool.pop()
                    if len(selected_worker.orders) == 1 and selected_worker.orders[0].ability.id in [
                        AbilityId.HARVEST_RETURN
                    ]:
                        actions.append(selected_worker.move(geyser))
                        actions.append(selected_worker.return_resource(queue=True))
                    else:
                        actions.append(selected_worker.gather(geyser))

        for location, townhall in owned_expansions.items():
            actual = townhall.assigned_harvesters
            ideal = townhall.ideal_harvesters

            deficit = ideal - actual
            for _ in range(0, deficit):
                if worker_pool:
                    selected_worker = worker_pool.pop()
                    mineral_field = self.state.mineral_field.closest_to(townhall)
                    if len(selected_worker.orders) == 1 and selected_worker.orders[0].ability.id in [
                        AbilityId.HARVEST_RETURN
                    ]:
                        actions.append(selected_worker.move(townhall))
                        actions.append(selected_worker.return_resource(queue=True))
                        actions.append(selected_worker.gather(mineral_field, queue=True))
                    else:
                        actions.append(selected_worker.gather(mineral_field))

        await self.do_actions(actions)

    @property
    def owned_expansions(self):
        """List of expansions owned by the player."""

        owned = {}
        for exp_loc in self.expansion_locations:
            townhall = next((x for x in self.townhalls if self.is_near_to_expansion(x, exp_loc)), None)
            if townhall:
                owned[exp_loc] = townhall

        return owned

    def can_feed(self, unit_type: UnitTypeId) -> bool:
        """ Checks if you have enough free supply to build the unit """
        required = self._game_data.units[unit_type.value].proto.food_required
        return required == 0 or self.supply_left >= required

    def can_afford(
        self, item_id: Union[UnitTypeId, UpgradeId, AbilityId], check_supply_cost: bool = True
    ) -> "CanAffordWrapper":
        """Tests if the player has enough resources to build a unit or cast an ability."""
        enough_supply = True
        if isinstance(item_id, UnitTypeId):
            unit = self._game_data.units[item_id.value]
            cost = self._game_data.calculate_ability_cost(unit.creation_ability)
            if check_supply_cost:
                enough_supply = self.can_feed(item_id)
        elif isinstance(item_id, UpgradeId):
            cost = self._game_data.upgrades[item_id.value].cost
        else:
            cost = self._game_data.calculate_ability_cost(item_id)

        return CanAffordWrapper(cost.minerals <= self.minerals, cost.vespene <= self.vespene, enough_supply)

    async def can_cast(
        self,
        unit: Unit,
        ability_id: AbilityId,
        target: Optional[Union[Unit, Point2, Point3]] = None,
        only_check_energy_and_cooldown: bool = False,
        cached_abilities_of_unit: List[AbilityId] = None,
    ) -> bool:
        """Tests if a unit has an ability available and enough energy to cast it.
        See data_pb2.py (line 161) for the numbers 1-5 to make sense"""
        assert isinstance(unit, Unit)
        assert isinstance(ability_id, AbilityId)
        assert isinstance(target, (type(None), Unit, Point2, Point3))
        if cached_abilities_of_unit:
            abilities = cached_abilities_of_unit
        else:
            abilities = (await self.get_available_abilities([unit]))[0]

        if ability_id in abilities:
            if only_check_energy_and_cooldown:
                return True
            cast_range = self._game_data.abilities[ability_id.value].proto.cast_range
            ability_target = self._game_data.abilities[ability_id.value].proto.target
            if (
                ability_target == 1
                or ability_target == Target.PointOrNone.value
                and isinstance(target, (Point2, Point3))
                and unit.distance_to(target) <= cast_range
            ):
                return True
            if (
                ability_target in {Target.Unit.value, Target.PointOrUnit.value}
                and isinstance(target, Unit)
                and unit.distance_to(target) <= cast_range
            ):
                return True
            return (
                ability_target in {Target.Point.value, Target.PointOrUnit.value}
                and isinstance(target, (Point2, Point3))
                and unit.distance_to(target) <= cast_range
            )
        return False

    def select_build_worker(self, pos: Union[Unit, Point2, Point3], force: bool = False) -> Optional[Unit]:
        """Select a worker to build a bulding with."""
        workers = self.workers.closer_than(20, pos) or self.workers
        for worker in workers.prefer_close_to(pos).prefer_idle:
            if (
                not worker.orders
                or len(worker.orders) == 1
                and worker.orders[0].ability.id in [AbilityId.MOVE, AbilityId.HARVEST_GATHER, AbilityId.HARVEST_RETURN]
            ):
                return worker
        return workers.random if force else None

    async def can_place(self, building: Union[AbilityData, AbilityId, UnitTypeId], position: Point2) -> bool:
        """Tests if a building can be placed in the given location."""
        assert isinstance(building, (AbilityData, AbilityId, UnitTypeId))
        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        elif isinstance(building, AbilityId):
            building = self._game_data.abilities[building.value]
        placements = await self._client.query_building_placement(building, [position])
        return placements[0] == ActionResult.Success

    async def find_placement(
        self,
        building: UnitTypeId,
        near: Union[Unit, Point2, Point3],
        max_distance: int = 20,
        random_alternative: bool = True,
        placement_step: int = 2,
    ) -> Optional[Point2]:
        """Finds a placement location for building."""
        assert isinstance(building, (AbilityId, UnitTypeId))
        assert isinstance(near, Point2)
        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        else:
            building = self._game_data.abilities[building.value]
        if await self.can_place(building, near):
            return near
        if max_distance == 0:
            return None
        for distance in range(placement_step, max_distance, placement_step):
            possible_positions = [
                Point2(p).offset(near).to2
                for p in (
                    [(dx, -distance) for dx in range(-distance, distance + 1, placement_step)]
                    + [(dx, distance) for dx in range(-distance, distance + 1, placement_step)]
                    + [(-distance, dy) for dy in range(-distance, distance + 1, placement_step)]
                    + [(distance, dy) for dy in range(-distance, distance + 1, placement_step)]
                )
            ]
            res = await self._client.query_building_placement(building, possible_positions)
            possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success]
            if not possible:
                continue
            if random_alternative:
                return random.choice(possible)
            return min(possible, key=lambda p: p.distance_to(near))
        return None

    def already_pending_upgrade(self, upgrade_type: UpgradeId) -> Union[int, float]:
        """ Check if an upgrade is being researched
        Return values:
        0: not started
        0 < x < 1: researching
        1: finished
        """
        assert isinstance(upgrade_type, UpgradeId)
        if upgrade_type in self.state.upgrades:
            return 1
        creation_ability_id = self._game_data.upgrades[upgrade_type.value].research_ability.id
        for structure in self.units.structure.ready:
            for order in structure.orders:
                if order.ability.id == creation_ability_id:
                    return order.progress
        return 0

    def already_pending(self, unit_type: Union[UpgradeId, UnitTypeId], all_units: bool = False) -> int:
        """
        Returns a number of buildings or units already in progress, or if a
        worker is en route to build it. This also includes queued orders for
        workers and build queues of buildings.

        If all_units==True, then build queues of other units (such as Carriers
        (Interceptors) or Oracles (Stasis Ward)) are also included.
        """
        if isinstance(unit_type, UpgradeId):
            return self.already_pending_upgrade(unit_type)
        ability = self._game_data.units[unit_type.value].creation_ability
        amount = len(self.units(unit_type).not_ready)
        if all_units:
            amount += sum([o.ability == ability for u in self.units for o in u.orders])
        else:
            amount += sum([o.ability == ability for w in self.workers for o in w.orders])
            amount += sum([egg.orders[0].ability == ability for egg in self.units(UnitTypeId.EGG)])
        return amount

    async def build(
        self,
        building: UnitTypeId,
        near: Union[Point2, Point3],
        max_distance: int = 20,
        unit: Optional[Unit] = None,
        random_alternative: bool = True,
        placement_step: int = 2,
    ):
        """Build a building."""

        if isinstance(near, Unit):
            near = near.position.to2
        elif near is not None:
            near = near.to2
        possible_placements = await self.find_placement(
            building, near.rounded, max_distance, random_alternative, placement_step
        )
        if possible_placements is None:
            return ActionResult.CantFindPlacementLocation
        unit = unit or self.select_build_worker(possible_placements)
        if unit is None or not self.can_afford(building):
            return ActionResult.Error
        return await self.do(unit.build(building, possible_placements))

    async def do(self, action):
        """Execute the action"""
        if not self.can_afford(action):
            LOGGER.warning(f"Cannot afford action {action}")
            return ActionResult.Error
        possible_action = await self._client.actions(action, game_data=self._game_data)
        if not possible_action:
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene
        else:
            LOGGER.error(f"Error: {possible_action} (action: {action})")
        return possible_action

    async def do_actions(self, actions: List["UnitCommand"]):
        """Group all actions then execute all at the 'same' time"""
        if not actions:
            return None
        for action in actions:
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene
        action_queue = await self._client.actions(actions, game_data=self._game_data)
        return action_queue

    async def chat_send(self, message: str):
        """Send a chat message."""
        assert isinstance(message, str)
        await self._client.chat_send(message, False)

    def get_terrain_height(self, pos: Union[Point2, Point3, Unit]) -> int:
        """ Returns terrain height at a position. Caution: terrain height is not anywhere near a unit's z-coordinate."""
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.terrain_height[pos]

    def in_placement_grid(self, pos: Union[Point2, Point3, Unit]) -> bool:
        """ Returns True if you can place something at a position.
        Remember, buildings usually use 2x2, 3x3 or 5x5 of these grid points.
        Caution: some x and y offset might be required, see ramp code:
        https://github.com/Dentosal/python-sc2/blob/master/sc2/game_info.py#L17-L18 """
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.placement_grid[pos] != 0

    def in_pathing_grid(self, pos: Union[Point2, Point3, Unit]) -> bool:
        """ Returns True if a unit can pass through a grid point. """
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.pathing_grid[pos] == 0

    def is_visible(self, pos: Union[Point2, Point3, Unit]) -> bool:
        """ Returns True if you have vision on a grid point. """
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self.state.visibility[pos] == 2

    def has_creep(self, pos: Union[Point2, Point3, Unit]) -> bool:
        """ Returns True if there is creep on the grid point. """
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self.state.creep[pos]

    def prepare_start(self, client, player_id, game_info, game_data):
        """Ran until game start to set game and player data."""
        self._client: "Client" = client
        self._game_info: "GameInfo" = game_info
        self._game_data: GameData = game_data
        self.player_id: int = player_id
        self.race: Race = Race(self._game_info.player_races[self.player_id])
        self._units_previous_map: dict = dict()
        self.units: Units = Units([], game_data)

    def prepare_first_step(self):
        """First step extra preparations. Must not be called before _prepare_step."""
        if self.townhalls:
            self._game_info.player_start_location = self.townhalls.first.position
        self._game_info.map_ramps = self._game_info.find_ramps()

    def prepare_step(self, state):
        """Set attributes from new state before on_step."""
        self.state: GameState = state
        self._units_previous_map.clear()
        for unit in self.units:
            self._units_previous_map[unit.tag] = unit
        self.units: Units = state.units.owned
        self.workers: Units = self.units(race_worker[self.race])
        self.townhalls: Units = self.units(race_townhalls[self.race])
        self.geysers: Units = self.units(race_gas[self.race])
        self.minerals: Union[float, int] = state.common.minerals
        self.vespene: Union[float, int] = state.common.vespene
        self.supply_used: Union[float, int] = state.common.food_used
        self.supply_cap: Union[float, int] = state.common.food_cap
        self.supply_left: Union[float, int] = self.supply_cap - self.supply_used

    async def issue_events(self):
        """ This function will be automatically run from main.py and triggers the following functions:
        - on_unit_created
        - on_unit_destroyed
        - on_building_construction_complete
        """
        await self._issue_unit_dead_events()
        await self._issue_unit_added_events()
        for unit in self.units:
            await self._issue_building_complete_event(unit)

    async def _issue_unit_added_events(self):
        for unit in self.units:
            if unit.tag not in self._units_previous_map:
                await self.on_unit_created(unit)

    async def _issue_building_complete_event(self, unit):
        if unit.build_progress < 1:
            return
        if unit.tag not in self._units_previous_map:
            return
        unit_prev = self._units_previous_map[unit.tag]
        if unit_prev.build_progress < 1:
            await self.on_building_construction_complete(unit)

    async def _issue_unit_dead_events(self):
        event = self.state.observation.raw_data.event
        if event is not None:
            for tag in event.dead_units:
                await self.on_unit_destroyed(tag)

    async def on_unit_destroyed(self, unit_tag):
        """ Override this in your bot class. """
        pass

    async def on_unit_created(self, unit: Unit):
        """ Override this in your bot class. """
        pass

    async def on_building_construction_complete(self, unit: Unit):
        """ Override this in your bot class. """
        pass

    def on_start(self):
        """Allows initializing the bot when the game data is available."""
        pass

    async def on_step(self, iteration: int):
        """Ran on every game step (looped in realtime mode)."""
        raise NotImplementedError

    def on_end(self, game_result: Result):
        """Ran at the end of a game."""
        pass


class CanAffordWrapper:
    """Identifies if the bot can afford the action"""

    def __init__(self, can_afford_minerals, can_afford_vespene, have_enough_supply):
        self.can_afford_minerals = can_afford_minerals
        self.can_afford_vespene = can_afford_vespene
        self.have_enough_supply = have_enough_supply

    def __bool__(self):
        return self.can_afford_minerals and self.can_afford_vespene and self.have_enough_supply
