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
    ULTRALISK,
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
        self.targets = self.atk_force = self.hydra_targets = None

    async def should_handle(self):
        """Requirements to run handle"""
        return self.main.units.of_type({ZERGLING, HYDRALISK, MUTALISK, ULTRALISK})

    async def handle(self):
        """Run the logic for all unit types, it can be improved a lot but is already much better than a-move"""
        self.set_unit_groups()
        for attacking_unit in self.atk_force:
            # if self.dodge_effects(attacking_unit):
            #    continue
            if self.disruptor_dodge(attacking_unit):
                continue
            if self.anti_proxy_trigger(attacking_unit):
                if self.attack_enemy_proxy_units(attacking_unit):
                    continue
                self.main.add_action(attacking_unit.move(self.main.spines.closest_to(attacking_unit)))
                continue
            if self.anti_terran_bm(attacking_unit):
                continue
            if attacking_unit.tag in self.retreat_units:
                self.has_retreated(attacking_unit)
                continue
            if self.specific_hydra_behavior(self.hydra_targets, attacking_unit):
                continue
            if await self.specific_zergling_behavior(self.targets, attacking_unit):
                continue
            if self.target_buildings(attacking_unit):
                continue
            if not self.main.close_enemies_to_base:
                self.idle_unit(attacking_unit)
                continue
            if self.keep_attacking(attacking_unit):
                continue
            self.move_to_rallying_point(self.targets, attacking_unit)

    def has_retreated(self, unit):
        """Identify if the unit has retreated(a little bugged it doesn't always clean it)"""
        if self.main.townhalls.closer_than(15, unit.position):
            self.retreat_units.remove(unit.tag)

    def idle_unit(self, unit):
        """Control the idle units, by gathering then or telling then to attack"""
        if (
            self.main.townhalls
            and not self.main.counter_attack_vs_flying
            and self.gathering_force_value(1, 2, 4) < 42
            and self.retreat_units
        ):
            self.move_to_rallying_point(self.targets, unit)
            return True
        if not self.main.close_enemy_production or self.main.time >= 480:
            if self.main.townhalls:
                self.attack_closest_building(unit)
            return self.attack_start_location(unit)
        return False

    def attack_closest_building(self, unit):
        """Attack the closest enemy building"""
        enemy_building = self.main.enemy_structures.not_flying
        if enemy_building:
            self.main.add_action(unit.attack(enemy_building.closest_to(self.main.furthest_townhall_to_center)))

    def anti_proxy_trigger(self, unit):
        """Requirements for the anti-proxy logic"""
        return (
            self.main.close_enemy_production
            and self.main.spines
            and (self.main.time <= 480 or self.main.zergling_amount <= 14)
            and not self.main.spines.closer_than(2, unit)
        )

    def attack_enemy_proxy_units(self, unit):
        """Requirements to attack the proxy army if it gets too close to the ramp"""
        return (
            self.targets
            and unit.type_id == ZERGLING
            and self.targets.closer_than(5, unit)
            and self.micro_zerglings(unit, self.targets)
        )

    def set_unit_groups(self):
        """Set the targets and atk_force, separating then by type"""
        if self.main.enemies:
            excluded_units = {ADEPTPHASESHIFT, DISRUPTORPHASED, EGG, LARVA, INFESTEDTERRANSEGG, INFESTEDTERRAN}
            filtered_enemies = self.main.enemies.not_structure.exclude_type(excluded_units)
            static_defence = self.main.enemy_structures.of_type(
                {SPINECRAWLER, PHOTONCANNON, BUNKER, PLANETARYFORTRESS, AUTOTURRET}
            )
            self.targets = static_defence | filtered_enemies.not_flying
            self.hydra_targets = static_defence | filtered_enemies.filter(lambda unit: not unit.is_snapshot)
        self.atk_force = self.main.units.of_type({HYDRALISK, MUTALISK, ULTRALISK}) | self.main.zerglings
        if self.main.floating_buildings_bm and self.main.supply_used >= 199:
            self.atk_force = self.atk_force | self.main.queens

    def anti_terran_bm(self, unit):
        """Logic for countering the floating buildings bm"""
        if unit.type_id in (MUTALISK, QUEEN, HYDRALISK) and self.main.enemy_structures.flying:
            self.main.add_action(unit.attack(self.main.enemy_structures.flying.closest_to(unit.position)))
            return True
        return False

    def keep_attacking(self, unit):
        """It keeps the attack going if it meets the requirements no matter what"""
        if not self.retreat_units or self.main.close_enemies_to_base:
            if self.main.enemy_structures:
                self.main.add_action(unit.attack(self.main.enemy_structures.closest_to(unit.position)))
                return True
            if self.targets:
                self.main.add_action(unit.attack(self.targets.closest_to(unit.position)))
                return True
            return False
        return False

    def target_buildings(self, unit):
        """Target close buildings if any other target is available"""
        if self.main.enemy_structures.closer_than(30, unit.position):
            self.main.add_action(unit.attack(self.main.enemy_structures.closest_to(unit.position)))
            return True
        return False
