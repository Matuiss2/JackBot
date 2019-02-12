"""Everything related to queen abilities and distribution goes here"""
from sc2.constants import EFFECT_INJECTLARVA, QUEENSPAWNLARVATIMER


class QueensAbilities:
    """Can be improved(Defense not utility), cancel other orders so it can defend better"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirement to run the queen distribution and actions"""
        return self.main.queens and self.main.townhalls

    async def handle(self):
        """Assign a queen to each base to make constant injections and the extras for creep spread
        Injection and creep spread are ok, can be expanded so it accepts transfusion and micro"""
        actions = self.main.add_action  # added to save line breaks
        if not (self.main.floating_buildings_bm and self.main.supply_used >= 199):
            for queen in self.main.queens.idle:
                selected_base = self.main.townhalls.closest_to(queen.position)
                if queen.energy >= 25 and not selected_base.has_buff(QUEENSPAWNLARVATIMER):
                    actions(queen(EFFECT_INJECTLARVA, selected_base))
                    continue
                elif queen.energy >= 25:
                    await self.main.place_tumor(queen)
            for base in self.main.townhalls.ready.idle:
                if not self.main.queens.closer_than(4, base):
                    for queen in self.main.queens:
                        if self.main.enemies.not_structure.closer_than(10, queen.position):
                            actions(queen.attack(self.main.enemies.not_structure.closest_to(queen.position)))
                            continue
                        if queen.is_moving and self.main.close_enemies_to_base:
                            actions(queen.stop())
                            continue
                        if not self.main.townhalls.closer_than(4, queen):
                            actions(queen.move(base.position))
            return True
