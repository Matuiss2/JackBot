"""Every helper for controlling units go here"""


class Micro:
    """Group all helpers, for unit control and targeting here"""

    def attack_close_target(self, unit, enemies):
        """It targets lowest hp units on its range, if there is any, attack the closest"""
        targets_close = enemies.in_attack_range_of(unit)
        if targets_close:
            self.attack_lowhp(unit, targets_close)
            return True
        buildings_in_attack_range = self.ai.known_enemy_units.in_attack_range_of(unit)
        if buildings_in_attack_range:
            self.attack_lowhp(unit, buildings_in_attack_range)
            return True
        target = enemies.closest_to(unit)
        if target:
            self.ai.add_action(unit.attack(target))
            return True
        return None

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
