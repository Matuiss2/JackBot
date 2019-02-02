"""Every helper for controlling units go here"""
from sc2.constants import (
    DISRUPTORPHASED,
    # GUARDIANSHIELDPERSISTENT,
    # LIBERATORTARGETMORPHDELAYPERSISTENT,
    # LIBERATORTARGETMORPHPERSISTENT,
    # SCANNERSWEEP,
    ULTRALISK,
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
        local_controller = self.controller
        if not local_controller.state.effects or unit.type_id == ULTRALISK:
            return False
        excluded_effects = (
            SCANNERSWEEP,
            GUARDIANSHIELDPERSISTENT,
            LIBERATORTARGETMORPHDELAYPERSISTENT,
            LIBERATORTARGETMORPHPERSISTENT,
        )  # Placeholder(must find better way to handle some of these)
        for effect in local_controller.state.effects:
            if effect.id in excluded_effects:
                continue
            danger_zone = effect.radius + unit.radius + 0.2
            if unit.position.distance_to_closest(effect.positions) > danger_zone:
                continue
            perimeter_of_effect = Point2.center(effect.positions).furthest(list(unit.position.neighbors8))
            local_controller.add_action(unit.move(perimeter_of_effect.towards(unit.position, -danger_zone)))
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
            self.controller.add_action(unit.attack(target))
            return True
        return None

    def attack_in_range(self, unit):
        """Attacks the lowest hp enemy in range of the unit"""
        target_in_range = filter_in_attack_range_of(unit, self.controller.enemies)
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
        self.controller.add_action(unit.move(self.closest_lowest_hp(unit, enemies)))

    def attack_lowhp(self, unit, enemies):
        """Attack enemy with lowest HP"""
        self.controller.add_action(unit.attack(self.closest_lowest_hp(unit, enemies)))

    @staticmethod
    def closest_lowest_hp(unit, enemies):
        """Find the closest within the lowest hp enemies"""
        return enemies.filter(lambda x: x.health == min(enemy.health for enemy in enemies)).closest_to(unit)

    def stutter_step(self, target, unit):
        """Attack when the unit can, run while it can't. We don't outrun the enemy."""
        action = self.controller.add_action
        if not unit.weapon_cooldown:
            action(unit.attack(target))
            return True
        retreat_point = self.find_retreat_point(target, unit)
        action(unit.move(retreat_point))
        return True

    def hit_and_run(self, target, unit, range_upgrade=None):
        """Attack when the unit can, run while it can't. We outrun the enemy."""
        # Only do this when our range > enemy range, our move speed > enemy move speed, and enemy is targeting us.
        action = self.controller.add_action
        unit_radius = unit.radius
        our_range = unit.ground_range
        partial_enemy_range = target.ground_range
        if not partial_enemy_range:
            partial_enemy_range = 0
        enemy_range = partial_enemy_range + target.radius
        if range_upgrade:
            our_range += 1
        # Our unit should stay just outside enemy range, and inside our range.
        if enemy_range:
            minimum_distance = enemy_range + unit_radius + 0.01
        else:
            minimum_distance = our_range - unit_radius
        if minimum_distance > our_range:  # Check to make sure this range isn't negative.
            minimum_distance = our_range - unit_radius - 0.01
        # If our unit is in that range, and our attack is at least halfway off cooldown, attack.
        if minimum_distance <= unit.distance_to(target) <= our_range and unit.weapon_cooldown <= 0.295 * 22.4:
            action(unit.attack(target))
            return True
        # If our unit is too close, or our weapon is on more than a quarter cooldown, run away.
        if unit.distance_to(target) < minimum_distance or unit.weapon_cooldown > 0.1475 * 22.4:
            retreat_point = self.find_retreat_point(target, unit)
            action(unit.move(retreat_point))
            return True
        pursuit_point = self.find_pursuit_point(target, unit)  # If our unit is too far, run towards.
        action(unit.move(pursuit_point))
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
        local_controller = self.controller
        if unit.type_id == ULTRALISK:
            return False
        for ball in local_controller.enemies.of_type(DISRUPTORPHASED):
            if ball.distance_to(unit) < 3:
                retreat_point = self.find_retreat_point(ball, unit)
                local_controller.add_action(unit.move(retreat_point))
                return True
        return None