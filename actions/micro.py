

class micro:
    def attack_close_target(self, unit, enemies):
        targets_close = enemies.in_attack_range_of(unit)
        if targets_close:
            self.attack_lowhp(unit, targets_close)
            return True
        else:
            target = enemies.closest_to(unit)
            if target:
                self.ai.actions.append(unit.attack(target))
                return True
        return False

    def move_to_next_target(self, unit, enemies):
        targets_in_range_1 = enemies.closer_than(1, unit)
        if targets_in_range_1:
            self.move_lowhp(unit, targets_in_range_1)
            return True
        return False

    def move_lowhp(self, unit, enemies):
        """Move to enemy with lowest HP"""
        target = self.closest_lowest_hp(unit, enemies)
        self.ai.actions.append(unit.move(target))

    def attack_lowhp(self, unit, enemies):
        """Attack enemy with lowest HP"""
        target = self.closest_lowest_hp(unit, enemies)
        self.ai.actions.append(unit.attack(target))

    def closest_lowest_hp(self, unit, enemies):
        lowest_unit = self.lowest_hp(enemies)
        return lowest_unit.closest_to(unit)

    def lowest_hp(self, enemies):
        lowesthp = min(unit.health for unit in enemies)
        low_enemies = enemies.filter(lambda x: x.health == lowesthp)
        return low_enemies
