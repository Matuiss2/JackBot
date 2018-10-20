"""Everything related to queen abilities and distribution goes here"""
from sc2.constants import EFFECT_INJECTLARVA, QUEENSPAWNLARVATIMER


class QueensAbilities:
    """Can be improved(Defense not utility)"""

    def __init__(self, ai):
        self.ai = ai
        self.queens = None
        self.hatchery = None
        self.enemies = None

    async def should_handle(self, iteration):
        """Injection and creep spread, can be expanded so it accepts transfusion"""
        self.queens = self.ai.queens
        self.hatchery = self.ai.townhalls
        self.enemies = self.ai.known_enemy_units.not_structure

        if not self.queens:
            return False

        if not self.hatchery:
            return False

        return True

    async def handle(self, iteration):
        """Assign a queen to each base to make constant injections and the extras for creep spread"""
        if not (self.ai.floating_buildings_bm and self.ai.supply_used >= 199):
            action = self.ai.add_action
            for queen in self.queens.idle:
                queen_position = queen.position
                queen_energy = queen.energy
                if self.enemies.closer_than(10, queen_position):
                    action(queen.attack(self.enemies.closest_to(queen_position)))
                    continue
                selected = self.hatchery.closest_to(queen.position)
                if queen_energy >= 25 and not selected.has_buff(QUEENSPAWNLARVATIMER):
                    action(queen(EFFECT_INJECTLARVA, selected))
                    continue
                elif queen_energy >= 25:
                    await self.ai.place_tumor(queen)

            for hatch in self.hatchery.ready.noqueue:
                if not self.queens.closer_than(4, hatch):
                    for queen in self.queens.idle:
                        if not self.ai.townhalls.closer_than(4, queen):
                            action(queen.move(hatch.position))
                            break

            return True
