"""Everything related to controlling army units goes here"""
from sc2 import Race
from sc2.constants import (
    ADEPTPHASESHIFT,
    AUTOTURRET,
    BUNKER,
    DISRUPTORPHASED,
    EGG,
    EVOLVEGROOVEDSPINES,
    EVOLVEMUSCULARAUGMENTS,
    HYDRALISK,
    INFESTEDTERRAN,
    INFESTEDTERRANSEGG,
    LARVA,
    MUTALISK,
    PHOTONCANNON,
    PLANETARYFORTRESS,
    QUEEN,
    SPINECRAWLER,
    ZERGLING,
    ZERGLINGATTACKSPEED,
)
from actions.micro.army_value_tables import EnemyArmyValue
from actions.micro.micro_helpers import Micro
from actions.micro.unit.hydralisks import HydraControl
from actions.micro.unit.zerglings import ZerglingControl


class ArmyControl(ZerglingControl, HydraControl, Micro, EnemyArmyValue):
    """Can be improved performance wise also few bugs on some of it's elements"""

    def __init__(self, main):
        self.controller = main
        self.retreat_units = set()
        self.baneling_sacrifices = {}
        self.rally_point = self.action = self.unit_position = self.attack_command = self.bases = None
        self.static_defence = None
        self.zergling_atk_speed = self.hydra_move_speed = self.hydra_atk_range = False

    async def should_handle(self):
        """Requirements to run handle"""
        return bool(
            self.controller.zerglings | self.controller.ultralisks | self.controller.mutalisks | self.controller.hydras
        )

    async def handle(self):
        """Run the logic for all unit types, it can be improved a lot but is already much better than a-move"""
        self.action = self.controller.add_action
        self.bases = self.controller.townhalls
        self.behavior_changing_upgrades_check()
        targets, atk_force, hydra_targets = self.set_unit_groups()
        for attacking_unit in atk_force:
            """if self.dodge_effects(attacking_unit):
                continue"""
            if self.disruptor_dodge(attacking_unit):
                continue
            self.unit_position = attacking_unit.position
            self.attack_command = attacking_unit.attack
            if self.anti_proxy_trigger(attacking_unit):
                if self.attack_enemy_proxy_units(targets, attacking_unit):
                    continue
                self.action(attacking_unit.move(self.controller.spines.closest_to(attacking_unit)))
                continue
            if self.anti_terran_bm(attacking_unit):
                continue
            if attacking_unit.tag in self.retreat_units and self.bases:
                self.has_retreated(attacking_unit)
                continue
            if self.specific_hydra_behavior(hydra_targets, attacking_unit):
                continue
            if await self.specific_zergling_behavior(targets, attacking_unit):
                continue
            enemy_building = self.controller.enemy_structures
            if enemy_building.closer_than(30, self.unit_position):
                self.action(self.attack_command(enemy_building.closest_to(self.unit_position)))
                continue
            if not self.controller.close_enemies_to_base:
                self.idle_unit(attacking_unit)
                continue
            if self.keep_attacking(attacking_unit, targets):
                continue
            self.move_to_rallying_point(attacking_unit)

    def move_to_rallying_point(self, unit):
        """Set the point where the units should gather"""
        map_center = self.controller.game_info.map_center
        if self.bases.ready:
            self.rally_point = self.bases.ready.closest_to(map_center).position.towards(map_center, 10)
        if unit.position.distance_to_point2(self.rally_point) > 5:
            self.action(unit.move(self.rally_point))

    def has_retreated(self, unit):
        """Identify if the unit has retreated(a little bugged it doesn't always clean it)"""
        if self.bases.closer_than(15, unit.position):
            self.retreat_units.remove(unit.tag)

    def retreat_unit(self, unit, target):
        """Tell the unit to retreat when overwhelmed"""
        if self.bases.closer_than(15, unit) or self.controller.counter_attack_vs_flying:
            return False
        if self.controller.enemy_race == Race.Zerg:
            enemy_value = self.enemy_value_zerg(unit, target)
        elif self.controller.enemy_race == Race.Terran:
            enemy_value = self.enemy_value_terran(unit, target)
        else:
            enemy_value = self.enemy_value_protoss(unit, target)
        if (
            self.bases
            and not self.controller.close_enemies_to_base
            and not self.controller.structures.closer_than(7, self.unit_position)
            and enemy_value >= self.battling_force_value(self.unit_position, 1, 5, 13)
        ):
            self.move_to_rallying_point(unit)
            self.retreat_units.add(unit.tag)
            return True
        return False

    def idle_unit(self, unit):
        """Control the idle units, by gathering then or telling then to attack"""
        if (
            self.gathering_force_value(1, 2, 4) < 42
            and self.bases
            and self.retreat_units
            and not self.controller.counter_attack_vs_flying
        ):
            self.move_to_rallying_point(unit)
            return True
        if not self.controller.close_enemy_production or self.controller.time >= 480:
            if self.bases:
                self.attack_closest_building(unit)
            return self.attack_start_location(unit)
        return False

    def attack_closest_building(self, unit):
        """Attack the closest enemy building"""
        enemy_building = self.controller.enemy_structures.not_flying.exclude_type(self.static_defence)
        if enemy_building:
            self.action(unit.attack(enemy_building.closest_to(self.controller.furthest_townhall_to_center)))

    def attack_start_location(self, unit):
        """It tell to attack the starting location"""
        if self.controller.enemy_start_locations and not self.controller.enemy_structures:
            self.action(unit.attack(self.controller.enemy_start_locations[0]))
            return True
        return False

    def anti_proxy_trigger(self, unit):
        """Requirements for the anti-proxy logic"""
        spines = self.controller.spines
        return (
            self.controller.close_enemy_production
            and spines
            and not spines.closer_than(2, unit)
            and (self.controller.time <= 480 or len(self.controller.zerglings) <= 14)
        )

    def attack_enemy_proxy_units(self, targets, unit):
        """Requirements to attack the proxy army if it gets too close to the ramp"""
        return (
            targets
            and targets.closer_than(5, unit)
            and unit.type_id == ZERGLING
            and self.micro_zerglings(unit, targets)
        )

    def set_unit_groups(self):
        """Set the targets and atk_force, separating then by type"""
        targets = hydra_targets = None
        enemy_units = self.controller.enemies
        enemy_building = self.controller.enemy_structures
        if enemy_units:
            excluded_units = {ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, LARVA, INFESTEDTERRANSEGG, INFESTEDTERRAN}
            filtered_enemies = enemy_units.not_structure.exclude_type(excluded_units)
            self.static_defence = enemy_building.of_type(
                {SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS, AUTOTURRET}
            )
            targets = self.static_defence | filtered_enemies.not_flying
            hydra_targets = self.static_defence | filtered_enemies
        atk_force = (
            self.controller.zerglings | self.controller.ultralisks | self.controller.mutalisks | self.controller.hydras
        )
        if self.controller.floating_buildings_bm and self.controller.supply_used >= 199:
            atk_force = atk_force | self.controller.queens
        return targets, atk_force, hydra_targets

    def anti_terran_bm(self, unit):
        """Logic for countering the floating buildings bm"""
        flying_buildings = self.controller.enemy_structures.flying
        if unit.type_id in (MUTALISK, QUEEN, HYDRALISK) and flying_buildings:
            self.action(unit.attack(flying_buildings.closest_to(self.unit_position)))
            return True
        return False

    async def handling_walls_and_attacking(self, unit, target):
        """It micros normally if no wall, if there is one attack it
        (can be improved, it does whats expected but its a regression overall when there is no walls)"""
        closest_target = target.closest_to
        if await self.controller._client.query_pathing(unit, closest_target(unit).position):
            if unit.type_id == ZERGLING:
                return self.micro_zerglings(unit, target)
            self.action(self.attack_command(closest_target(self.unit_position)))
            return True
        self.action(self.attack_command(self.controller.enemies.not_flying.closest_to(self.unit_position)))
        return True

    def keep_attacking(self, unit, target):
        """It keeps the attack going if it meets the requirements no matter what"""
        self.controller = self.controller
        enemy_building = self.controller.enemy_structures
        if not self.retreat_units or self.controller.close_enemies_to_base:
            if enemy_building:
                self.action(self.attack_command(enemy_building.closest_to(self.unit_position)))
                return True
            if target:
                self.action(self.attack_command(target.closest_to(self.unit_position)))
                return True
            return self.attack_start_location(unit)
        return False

    def specific_hydra_behavior(self, hydra_targets, unit):
        """Group everything related to hydras behavior on attack"""
        close_hydra_targets = None
        if hydra_targets:
            close_hydra_targets = hydra_targets.closer_than(20, self.unit_position)
        if unit.type_id == HYDRALISK and close_hydra_targets:
            if self.retreat_unit(unit, close_hydra_targets):
                return True
            if self.micro_hydras(hydra_targets, unit):
                return True
            return False
        return False

    async def specific_zergling_behavior(self, targets, unit):
        """Group everything related to zergling behavior on attack"""
        close_targets = None
        if targets:
            close_targets = targets.closer_than(20, self.unit_position)
        if close_targets:
            if self.retreat_unit(unit, close_targets):
                return True
            if await self.handling_walls_and_attacking(unit, close_targets):
                return True
            return False
        return False

    def behavior_changing_upgrades_check(self):
        """Check for upgrades that will change how the units behavior are calculated"""
        if not self.zergling_atk_speed and self.controller.hives:
            self.zergling_atk_speed = self.controller.already_pending_upgrade(ZERGLINGATTACKSPEED) == 1
        if not self.hydra_move_speed and self.controller.hydradens:
            self.hydra_move_speed = self.controller.already_pending_upgrade(EVOLVEMUSCULARAUGMENTS) == 1
        if not self.hydra_atk_range and self.controller.hydradens:
            self.hydra_atk_range = self.controller.already_pending_upgrade(EVOLVEGROOVEDSPINES) == 1
