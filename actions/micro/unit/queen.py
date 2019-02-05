"""Everything related to queen abilities and distribution goes here"""
from sc2.constants import EFFECT_INJECTLARVA, QUEENSPAWNLARVATIMER


class QueensAbilities:
    """Can be improved(Defense not utility), cancel other orders so it can defend better"""

    def __init__(self, main):
        self.main = main
        self.queens = self.bases = None

    async def should_handle(self):
        """Requirement to run the queen distribution and actions"""
        self.queens = self.main.queens
        self.bases = self.main.townhalls
        return bool(self.queens and self.bases)

    async def handle(self):
        """Assign a queen to each base to make constant injections and the extras for creep spread
        Injection and creep spread are ok, can be expanded so it accepts transfusion and micro"""
        if not (self.main.floating_buildings_bm and self.main.supply_used >= 199):
            action = self.main.add_action
            for queen in self.queens.idle:
                enemies = self.main.enemies.not_structure
                if enemies.closer_than(10, queen.position):
                    action(queen.attack(enemies.closest_to(queen.position)))
                    continue
                selected_base = self.bases.closest_to(queen.position)
                if queen.energy >= 25 and not selected_base.has_buff(QUEENSPAWNLARVATIMER):
                    action(queen(EFFECT_INJECTLARVA, selected_base))
                    continue
                elif queen.energy >= 25:
                    await self.main.place_tumor(queen)
            for base in self.bases.ready.noqueue:
                if not self.queens.closer_than(4, base):
                    for queen in self.queens.idle:
                        if not self.bases.closer_than(4, queen):
                            action(queen.move(base.position))
                            break
            return True
