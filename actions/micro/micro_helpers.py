"""Every helper for controlling units go here"""
from sc2 import Race
from sc2.constants import (
    DISRUPTORPHASED,
    # GUARDIANSHIELDPERSISTENT,
    # LIBERATORTARGETMORPHDELAYPERSISTENT,
    # LIBERATORTARGETMORPHPERSISTENT,
    # SCANNERSWEEP,
    ULTRALISK,
    ZERGLING,
)
from sc2.position import Point2

# from sc2.unit import Unit


def filter_in_attack_range_of(unit, targets):
    """filter targets who are in attack range of the unit"""
    return targets.subgroup(target for target in targets if unit.target_in_range(target))


class Micro:
    """Group all helpers, for unit control and targeting here"""

    # TODO - fix
    '''def dodge_effects(self, unit: Unit) -> bool:
        """Dodge any effects"""
        if not self.main.state.effects or unit.type_id == ULTRALISK:
            return False
        excluded_effects = (
            SCANNERSWEEP,
            GUARDIANSHIELDPERSISTENT,
            LIBERATORTARGETMORPHDELAYPERSISTENT,
            LIBERATORTARGETMORPHPERSISTENT,
        )  # Placeholder(must find better way to handle some of these)
        for effect in self.main.state.effects:
            if effect.id in excluded_effects:
                continue
            danger_zone = effect.radius + unit.radius + 0.2
            if unit.position.distance_to_closest(effect.positions) > danger_zone:
                continue
            perimeter_of_effect = Point2.center(effect.positions).furthest(list(unit.position.neighbors8))
            self.main.add_action(unit.move(perimeter_of_effect.towards(unit.position, -danger_zone)))
            return True
        return False'''

    def attack_close_target(self, unit, enemies):
        """It targets lowest hp units on its range, if there is any attack the closest"""
        targets_close = filter_in_attack_range_of(unit, enemies)
        if targets_close:
            self.attack_lowhp(unit, targets_close)
            return True
        if self.attack_in_range(unit):
            return True
        target = enemies.closest_to(unit)
        if target:
            self.main.add_action(unit.attack(target))
            return True
        return None

    def attack_in_range(self, unit):
        """Attacks the lowest hp enemy in range of the unit"""
        target_in_range = filter_in_attack_range_of(unit, self.main.enemies)
        if target_in_range:
            self.attack_lowhp(unit, target_in_range)
            return True
        return False

    def move_to_next_target(self, unit, enemies):
        """It helps on the targeting and positioning on the attack"""
        targets_in_range_1 = enemies.closer_than(1, unit)
        if targets_in_range_1:
            self.move_lowhp(unit, targets_in_range_1)
            return True
        return None

    def move_lowhp(self, unit, enemies):
        """Move to enemy with lowest HP"""
        self.main.add_action(unit.move(self.closest_lowest_hp(unit, enemies)))

    def attack_lowhp(self, unit, enemies):
        """Attack enemy with lowest HP"""
        self.main.add_action(unit.attack(self.closest_lowest_hp(unit, enemies)))

    @staticmethod
    def closest_lowest_hp(unit, enemies):
        """Find the closest within the lowest hp enemies"""
        return enemies.filter(lambda x: x.health == min(enemy.health for enemy in enemies)).closest_to(unit)

    def stutter_step(self, target, unit):
        """Attack when the unit can, run while it can't. We don't outrun the enemy."""
        action = self.main.add_action
        if not unit.weapon_cooldown:
            action(unit.attack(target))
            return True
        retreat_point = self.find_retreat_point(target, unit)
        action(unit.move(retreat_point))
        return True

    def hit_and_run(self, target, unit, range_upgrade=None):
        """Attack when the unit can, run while it can't. We outrun the enemy."""
        # Only do this when our range > enemy range, our move speed > enemy move speed, and enemy is targeting us.
        our_range = unit.ground_range
        partial_enemy_range = target.ground_range
        if not partial_enemy_range:  # If target is melee it returns None so to avoid crashes we convert it to integer
            partial_enemy_range = 0
        enemy_range = partial_enemy_range + target.radius
        if range_upgrade:
            our_range += 1
        # Our unit should stay just outside enemy range, and inside our range.
        if enemy_range:
            minimum_distance = enemy_range + unit.radius + 0.01
        else:
            minimum_distance = our_range - unit.radius
        if minimum_distance > our_range:  # Check to make sure this range isn't negative.
            minimum_distance = our_range - unit.radius - 0.01
        # If our unit is in that range, and our attack is at least halfway off cooldown, attack.
        if minimum_distance <= unit.distance_to(target) <= our_range and unit.weapon_cooldown <= 6.4:
            self.main.add_action(unit.attack(target))
            return True
        # If our unit is too close, or our weapon is on more than a quarter cooldown, run away.
        if unit.distance_to(target) < minimum_distance or unit.weapon_cooldown > 3.4:
            retreat_point = self.find_retreat_point(target, unit)
            self.main.add_action(unit.move(retreat_point))
            return True
        pursuit_point = self.find_pursuit_point(target, unit)  # If our unit is too far, run towards.
        self.main.add_action(unit.move(pursuit_point))
        return True

    @staticmethod
    def find_pursuit_point(target, unit) -> Point2:
        """Find a point towards the enemy unit"""
        unit_position = unit.position
        difference = unit_position - target.position
        return Point2((unit_position.x + (difference.x / 2) * -1, unit_position.y + (difference.y / 2) * -1))

    @staticmethod
    def find_retreat_point(target, unit) -> Point2:
        """Find a point away from the enemy unit"""
        difference = unit.position - target.position
        return Point2((unit.position.x + (difference.x / 2), unit.position.y + (difference.y / 2)))

    @staticmethod
    def trigger_threats(targets, unit, trigger_range):
        """Identify threats based on range"""
        for enemy in targets:
            if enemy.distance_to(unit) < trigger_range:
                yield enemy

    def disruptor_dodge(self, unit):
        """If the enemy has disruptor's, run a dodging code."""
        if unit.type_id == ULTRALISK:
            return False
        for ball in self.main.enemies.of_type(DISRUPTORPHASED):
            if ball.distance_to(unit) < 4:
                retreat_point = self.find_retreat_point(ball, unit)
                self.main.add_action(unit.move(retreat_point))
                return True
        return None

    def retreat_unit(self, unit, target):
        """Tell the unit to retreat when overwhelmed"""
        if self.main.townhalls.closer_than(15, unit) or self.main.counter_attack_vs_flying:
            return False
        if self.main.enemy_race == Race.Zerg:
            enemy_value = self.enemy_value_zerg(unit, target)
        elif self.main.enemy_race == Race.Terran:
            enemy_value = self.enemy_value_terran(unit, target)
        else:
            enemy_value = self.enemy_value_protoss(unit, target)
        if (
            self.main.townhalls
            and not self.main.close_enemies_to_base
            and not self.main.structures.closer_than(7, unit.position)
            and enemy_value >= self.battling_force_value(unit.position, 1, 5, 13)
        ):
            self.move_to_rallying_point(unit)
            self.retreat_units.add(unit.tag)
            return True
        return False

    async def handling_walls_and_attacking(self, unit, target):
        """It micros normally if no wall, if there is one attack it
        (can be improved, it does whats expected but its a regression overall when there is no walls)"""
        closest_target = target.closest_to
        if await self.main._client.query_pathing(unit, closest_target(unit).position):
            if unit.type_id == ZERGLING:
                return self.micro_zerglings(unit, target)
            self.action(unit.attack(closest_target(unit.position)))
            return True
        self.main.add_action(unit.attack(self.main.enemies.not_flying.closest_to(unit.position)))
        return True
