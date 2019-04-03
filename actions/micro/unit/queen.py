"""Everything related to queen abilities and distribution goes here"""
from sc2.constants import AbilityId, BuffId


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
        if not (self.main.floating_buildings_bm and self.main.supply_used >= 199):
            await self.handle_queen_abilities()
            self.handle_queen_distribution()

    async def handle_queen_abilities(self):
        """Logic for queen abilities"""
        for queen in self.main.queens.idle:
            selected_base = self.main.townhalls.closest_to(queen.position)
            if queen.energy >= 25:
                if not selected_base.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                    self.main.add_action(queen(AbilityId.EFFECT_INJECTLARVA, selected_base))
                    continue
                await self.main.place_tumor(queen)

    def handle_queen_distribution(self):
        """Logic for distributing and attacking for queens - adding transfusion would be good"""
        for base in self.main.townhalls.ready.idle:
            if not self.main.queens.closer_than(5, base):
                for queen in self.main.queens:
                    if self.main.enemies.not_structure.closer_than(10, queen.position):
                        self.main.add_action(queen.attack(self.main.enemies.not_structure.closest_to(queen.position)))
                        continue
                    if queen.is_moving and self.main.close_enemies_to_base:
                        self.main.add_action(queen.stop())
                        continue
                    if not self.main.townhalls.closer_than(5, queen):
                        self.main.add_action(queen.move(base.position))
