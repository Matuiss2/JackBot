"""Every helper for controlling units go here"""
from sc2.position import Point2
from sc2.unit import Unit
from sc2.constants import GUARDIANSHIELDPERSISTENT, SCANNERSWEEP


def filter_in_attack_range_of(unit, targets):
    """filter targets who are in attack range of the unit"""
    return targets.subgroup(target for target in targets if unit.target_in_range(target))


class Micro:
    """Group all helpers, for unit control and targeting here"""

    def dodge_effects(self, unit: Unit) -> bool:
        """Dodge any effects"""
        if not self.ai.state.effects:
            return False
        for effect in self.ai.state.effects:
            if effect.id in (SCANNERSWEEP, GUARDIANSHIELDPERSISTENT):
                continue
            effect_data = self.ai.game_data.effects[effect.id]
            danger_zone = effect_data.radius + unit.radius + .1
            closest_effect_position_to_unit = unit.position.closest(effect.positions)
            if not unit.position.distance_to_point2(closest_effect_position_to_unit) < danger_zone:
                continue
            neighbors8_of_unit = list(unit.position.neighbors8)
            center_of_effect = Point2.center(effect.positions)
            furthest_neighbor_to_effect = center_of_effect.furthest(neighbors8_of_unit)
            move_away = -1 * danger_zone
            self.ai.add_action(unit.move(furthest_neighbor_to_effect.towards(unit.position, move_away)))
            return True
        return False

    def attack_close_target(self, unit, enemies):
        """It targets lowest hp units on its range, if there is any, attack the closest"""
        targets_close = filter_in_attack_range_of(unit, enemies)
        if targets_close:
            self.attack_lowhp(unit, targets_close)
            return True
        if self.attack_in_range(unit):
            return True
        target = enemies.closest_to(unit)
        if target:
            self.ai.add_action(unit.attack(target))
            return True
        return None

    def attack_in_range(self, unit):
        """Attacks the lowest hp enemy in range of the unit"""
        target_in_range = filter_in_attack_range_of(unit, self.ai.enemies)
        if target_in_range:
            self.attack_lowhp(unit, target_in_range)
            return True
        return False

    def move_to_next_target(self, unit, enemies):
        """It helps on the targeting and positioning"""
        targets_in_range_1 = enemies.closer_than(1, unit)
        if targets_in_range_1:
            self.move_lowhp(unit, targets_in_range_1)
            return True
        return None

    def move_lowhp(self, unit, enemies):
        """Move to enemy with lowest HP"""
        target = self.closest_lowest_hp(unit, enemies)
        self.ai.add_action(unit.move(target))

    def attack_lowhp(self, unit, enemies):
        """Attack enemy with lowest HP"""
        target = self.closest_lowest_hp(unit, enemies)
        self.ai.add_action(unit.attack(target))

    def closest_lowest_hp(self, unit, enemies):
        """Find the closest of the lowest hp enemies"""
        lowest_unit = self.lowest_hp(enemies)
        return lowest_unit.closest_to(unit)

    @staticmethod
    def lowest_hp(enemies):
        """returns all of the units who share the lowest hp """
        lowesthp = min(unit.health for unit in enemies)
        low_enemies = enemies.filter(lambda x: x.health == lowesthp)
        return low_enemies

    def stutter_step(self, target, unit):
        """Attack when the unit can, run while it can't. We don't outrun the enemy."""
        local_controller = self.ai
        action = local_controller.add_action
        if not unit.weapon_cooldown:
            action(unit.attack(target))
            return True
        retreat_point = self.find_retreat_point(target, unit)
        action(unit.move(retreat_point))
        return True

    def hit_and_run(self, target, unit, range_upgrade=None):
        """Attack when the unit can, run while it can't. We outrun the enemy."""
        # Only do this when our range > enemy range, our movespeed > enemy movespeed, and enemy is targeting us.
        local_controller = self.ai
        action = local_controller.add_action
        our_range = unit.ground_range + unit.radius
        enemy_range = target.ground_range + target.radius
        if range_upgrade:
            our_range += 1
        # Our unit should stay just outside enemy range, and inside our range.
        if enemy_range:
            minimum_distance = enemy_range + unit.radius + 0.1
        else:
            minimum_distance = our_range - unit.radius
        # Check to make sure this range isn't negative.
        if minimum_distance > our_range:
            minimum_distance = our_range - unit.radius
        # If our unit is in that range, and our attack is at least halfway off cooldown, attack.
        if minimum_distance <= unit.distance_to(target) <= our_range and unit.weapon_cooldown <= 0.13:
            action(unit.attack(target))
            return True
        # If our unit is too close, or our weapon is on more than one quarter cooldown, run away.
        if unit.distance_to(target) < minimum_distance or unit.weapon_cooldown > 0.13:
            retreat_point = self.find_retreat_point(target, unit)
            action(unit.move(retreat_point))
            return True
        # If our unit is too far, run towards.
        pursuit_point = self.find_pursuit_point(target, unit)
        action(unit.move(pursuit_point))
        return True

    @staticmethod
    def find_pursuit_point(target, unit) -> Point2:
        """Find a point towards the enemy unit"""
        difference = unit.position - target.position
        return Point2((unit.position.x + (difference.x / 2) * -1, unit.position.y + (difference.y / 2) * -1))

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
