"""Every helper for controlling units go here"""
from sc2.position import Point2
from sc2.unit import Unit
from sc2.constants import GUARDIANSHIELDPERSISTENT

def filter_in_attack_range_of(unit, targets):
    """filter targets who are in attack range of the unit"""
    return targets.subgroup([target for target in targets if unit.target_in_range(target)])


class Micro:
    """Group all helpers, for unit control and targeting here"""

    def dodge_effects(self, unit: Unit) -> bool:
        """Dodge any effects"""
        if not self.ai.state.effects:
            return False
        for effect in self.ai.state.effects:
            if effect.id == GUARDIANSHIELDPERSISTENT:
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
