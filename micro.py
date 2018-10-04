

class micro:
    def attack_close_target(self, unit, enemies):
        targets_close = enemies.in_attack_range_of(unit)
        if targets_close:
            self.attack_lowhp(unit, targets_close)
        else:
            target = enemies.closest_to(unit)
            if target:
                self.actions.append(unit.attack(target))

    def move_to_next_target(self, unit, enemies):
        targets_in_range_1 = enemies.closer_than(1, unit)
        if targets_in_range_1:
            self.move_lowhp(unit, targets_in_range_1)
        else:
            self.move_lowhp(unit, enemies)

    def lowest_hp(self, units):
        lowesthp = min(unit.health for unit in units)
        low_enemies = units.filter(lambda x: x.health == lowesthp)
        return low_enemies

    def closest_lowest_hp(self, unit, units):
        lowest_unit = self.lowest_hp(units)
        return lowest_unit.closest_to(unit)

    def move_lowhp(self, unit, enemies):
        """Move to enemy with lowest HP"""
        target = self.closest_lowest_hp(unit, enemies)
        self.actions.append(unit.move(target))

    def attack_lowhp(self, unit, enemies):
        """Attack enemy with lowest HP"""
        target = self.closest_lowest_hp(unit, enemies)
        self.actions.append(unit.attack(target))
