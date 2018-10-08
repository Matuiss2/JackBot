from sc2.constants import EFFECT_INJECTLARVA, QUEENSPAWNLARVATIMER


class QueensAbilities:
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
        for queen in self.queens.idle:
            if self.enemies.closer_than(8, queen.position):
                self.ai.actions.append(queen.attack(self.enemies.closest_to(queen.position)))
                continue
            selected = self.hatchery.closest_to(queen.position)
            if queen.energy >= 25 and self.ai.tumors and not selected.has_buff(QUEENSPAWNLARVATIMER):
                self.ai.actions.append(queen(EFFECT_INJECTLARVA, selected))
                continue
            elif queen.energy >= 25:
                await self.ai.place_tumor(queen)

        for hatch in self.hatchery.ready.noqueue:
            if not self.queens.closer_than(4, hatch):
                for queen in self.queens.idle:
                    if not self.ai.townhalls.closer_than(4, queen):
                        self.ai.actions.append(queen.move(hatch.position))
                        break

        return True