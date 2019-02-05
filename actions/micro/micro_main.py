"""Everything related to controlling army units goes here"""
from sc2.constants import (
    ADEPTPHASESHIFT,
    AUTOTURRET,
    BUNKER,
    DISRUPTORPHASED,
    EGG,
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
)
from actions.micro.army_value_tables import EnemyArmyValue
from actions.micro.unit.zerglings import ZerglingControl
from actions.micro.specific_unit_behaviors import UnitsBehavior


class ArmyControl(ZerglingControl, UnitsBehavior, EnemyArmyValue):
    """Can be improved performance wise also few bugs on some of it's elements"""

    def __init__(self, main):
        self.main = main
        self.retreat_units = set()
        self.baneling_sacrifices = {}
        self.bases = self.static_defence = self.action = None

    async def should_handle(self):
        """Requirements to run handle"""
        return bool(self.main.zerglings | self.main.ultralisks | self.main.mutalisks | self.main.hydras)

    async def handle(self):
        """Run the logic for all unit types, it can be improved a lot but is already much better than a-move"""
        self.bases = self.main.townhalls
        self.action = self.main.add_action
        targets, atk_force, hydra_targets = self.set_unit_groups()
        for attacking_unit in atk_force:
            """if self.dodge_effects(attacking_unit):
                continue"""
            if self.disruptor_dodge(attacking_unit):
                continue
            if self.anti_proxy_trigger(attacking_unit):
                if self.attack_enemy_proxy_units(targets, attacking_unit):
                    continue
                self.action(attacking_unit.move(self.main.spines.closest_to(attacking_unit)))
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
            enemy_building = self.main.enemy_structures
            if enemy_building.closer_than(30, attacking_unit.position):
                self.action(attacking_unit.attack(enemy_building.closest_to(attacking_unit.position)))
                continue
            if not self.main.close_enemies_to_base:
                self.idle_unit(attacking_unit)
                continue
            if self.keep_attacking(attacking_unit, targets):
                continue
            self.move_to_rallying_point(attacking_unit)

    def move_to_rallying_point(self, unit):
        """Set the point where the units should gather"""
        map_center = self.main.game_info.map_center
        rally_point = self.bases.ready.closest_to(map_center).position.towards(map_center, 10)
        if unit.position.distance_to_point2(rally_point) > 5 and self.bases.ready:
            self.action(unit.move(rally_point))

    def has_retreated(self, unit):
        """Identify if the unit has retreated(a little bugged it doesn't always clean it)"""
        if self.bases.closer_than(15, unit.position):
            self.retreat_units.remove(unit.tag)

    def idle_unit(self, unit):
        """Control the idle units, by gathering then or telling then to attack"""
        if (
            self.gathering_force_value(1, 2, 4) < 42
            and self.bases
            and self.retreat_units
            and not self.main.counter_attack_vs_flying
        ):
            self.move_to_rallying_point(unit)
            return True
        if not self.main.close_enemy_production or self.main.time >= 480:
            if self.bases:
                self.attack_closest_building(unit)
            return self.attack_start_location(unit)
        return False

    def attack_closest_building(self, unit):
        """Attack the closest enemy building"""
        enemy_building = self.main.enemy_structures.not_flying.exclude_type(self.static_defence)
        if enemy_building:
            self.action(unit.attack(enemy_building.closest_to(self.main.furthest_townhall_to_center)))

    def attack_start_location(self, unit):
        """It tell to attack the starting location"""
        if self.main.enemy_start_locations and not self.main.enemy_structures:
            self.action(unit.attack(self.main.enemy_start_locations[0]))
            return True
        return False

    def anti_proxy_trigger(self, unit):
        """Requirements for the anti-proxy logic"""
        spines = self.main.spines
        return (
            self.main.close_enemy_production
            and spines
            and not spines.closer_than(2, unit)
            and (self.main.time <= 480 or self.main.zergling_amount <= 14)
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
        enemy_units = self.main.enemies
        enemy_building = self.main.enemy_structures
        if enemy_units:
            excluded_units = {ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, LARVA, INFESTEDTERRANSEGG, INFESTEDTERRAN}
            filtered_enemies = enemy_units.not_structure.exclude_type(excluded_units)
            self.static_defence = enemy_building.of_type(
                {SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS, AUTOTURRET}
            )
            targets = self.static_defence | filtered_enemies.not_flying
            hydra_targets = self.static_defence | filtered_enemies
        atk_force = self.main.zerglings | self.main.ultralisks | self.main.mutalisks | self.main.hydras
        if self.main.floating_buildings_bm and self.main.supply_used >= 199:
            atk_force = atk_force | self.main.queens
        return targets, atk_force, hydra_targets

    def anti_terran_bm(self, unit):
        """Logic for countering the floating buildings bm"""
        flying_buildings = self.main.enemy_structures.flying
        if unit.type_id in (MUTALISK, QUEEN, HYDRALISK) and flying_buildings:
            self.action(unit.attack(flying_buildings.closest_to(unit.position)))
            return True
        return False

    def keep_attacking(self, unit, target):
        """It keeps the attack going if it meets the requirements no matter what"""
        if not self.retreat_units or self.main.close_enemies_to_base:
            enemy_building = self.main.enemy_structures
            if enemy_building:
                self.action(unit.attack(enemy_building.closest_to(unit.position)))
                return True
            if target:
                self.action(unit.attack(target.closest_to(unit.position)))
                return True
            return self.attack_start_location(unit)
        return False
