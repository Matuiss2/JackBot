"""Everything related to the expansion logic goes here"""
from sc2.constants import UnitTypeId


class Expansion:
    """Can be improved"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Fourth base sometimes are not build at the expected time maybe reduce the lock for it,
         also maybe the 7th or more hatchery can be postponed for when extra mining patches or production are needed """
        if self.allow_expansion:
            if self.handle_mineral_overflow:
                return True
            if not self.main.hatcheries_in_queue:  # This is a mess and surely can be simplified
                base_amount = self.main.base_amount  # added to save lines
                if base_amount <= 5:
                    return self.main.zergling_amount >= 22 or self.main.time >= 285 if base_amount == 2 else True
                return self.main.caverns
            return False
        return False

    async def handle(self):
        """Expands to the nearest expansion location using the nearest drone to it"""
        drones = self.main.drones.gathering
        for expansion in self.main.ordered_expansions:
            if await self.main.can_place(UnitTypeId.HATCHERY, expansion):
                if not self.main.ground_enemies.closer_than(15, expansion) and drones:
                    self.main.add_action(drones.closest_to(expansion).build(UnitTypeId.HATCHERY, expansion))
                    break

    @property
    def allow_expansion(self):
        """ Check if its safe to expand and if we have the necessary minerals
         if its not don't even run the remaining expansion logic"""
        return (
            self.main.townhalls
            and self.main.can_afford(UnitTypeId.HATCHERY)
            and not self.main.close_enemies_to_base
            and (not self.main.close_enemy_production or self.main.time > 690)
        )

    @property
    def handle_mineral_overflow(self):
        """ When overflowing with minerals run this condition check"""
        return (
            self.main.minerals >= 900
            and self.main.hatcheries_in_queue < 2
            and self.main.base_amount + self.main.hatcheries_in_queue < len(self.main.expansion_locations)
            and self.main.base_amount > 4
        )
