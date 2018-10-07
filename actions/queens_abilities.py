from sc2.constants import CREEPTUMOR, CREEPTUMORBURROWED, CREEPTUMORQUEEN, EFFECT_INJECTLARVA, QUEENSPAWNLARVATIMER


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
        # lowhp_ultralisks = self.ai.ultralisks.filter(lambda lhpu: lhpu.health_percentage < 0.27)
        for queen in self.queens.idle:
            if self.enemies.closer_than(8, queen.position):
                self.ai.actions.append(queen.attack(self.enemies.closest_to(queen.position)))
                continue
            # if not lowhp_ultralisks.closer_than(8, queen.position):
            selected = self.hatchery.closest_to(queen.position)
            tumors = self.ai.units.of_type([CREEPTUMORQUEEN, CREEPTUMOR, CREEPTUMORBURROWED])
            if queen.energy >= 25 and tumors and not selected.has_buff(QUEENSPAWNLARVATIMER):
                self.ai.actions.append(queen(EFFECT_INJECTLARVA, selected))
                continue
            elif queen.energy >= 25:
                await self.ai.place_tumor(queen)

            # elif queen.energy >= 50:
            #     self.ai.actions.append(queen(TRANSFUSION_TRANSFUSION, lowhp_ultralisks.closest_to(queen.position)))

        for hatch in self.hatchery.ready.noqueue:
            if not self.queens.closer_than(4, hatch):
                for queen in self.queens.idle:
                    if not self.ai.townhalls.closer_than(4, queen):
                        self.ai.actions.append(queen.move(hatch.position))
                        break

        return True
