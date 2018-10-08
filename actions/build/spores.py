from sc2.constants import SPORECRAWLER


class BuildSpores:

    def __init__(self, ai):
        self.ai = ai
        self.selected_base = None
        self.enemy_flying_dmg_units = False

    async def should_handle(self, iteration):
        if not self.ai.pools.ready:
            return False

        if self.ai.known_enemy_units.flying:
            if [au for au in self.ai.known_enemy_units.flying if au.can_attack_ground]:
                self.enemy_flying_dmg_units = True

        base = self.ai.townhalls
        spores = self.ai.spores

        if not len(spores) < len(base.ready):
            return False

        self.selected_base = base.random
        return (
            (self.enemy_flying_dmg_units or self.ai.time >= 420)
            and not self.ai.already_pending(SPORECRAWLER)
            and not spores.closer_than(15, self.selected_base.position)
            and self.ai.can_afford(SPORECRAWLER)
        )

    async def handle(self, iteration):
        for base in self.ai.townhalls:
            spore_position = (
                (self.ai.state.mineral_field | self.ai.state.vespene_geyser)
                    .closer_than(10, base)
                    .center.towards(base, 1)
                )
            if not self.ai.spores.closer_than(15, spore_position):
                await self.ai.build(SPORECRAWLER, spore_position)
                return True