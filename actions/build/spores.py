from sc2.constants import SPORECRAWLER


class BuildSporse:

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
            self.enemy_flying_dmg_units
            and not self.ai.already_pending(SPORECRAWLER)
            and not spores.closer_than(15, self.selected_base.position)
            and self.ai.can_afford(SPORECRAWLER)
        )

    async def handle(self, iteration):
        await self.ai.build(SPORECRAWLER, near=self.selected_base.position)
        return True
