"""Everything related to building logic for the spores goes here"""
from sc2.constants import SPORECRAWLER


class BuildSpores:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.selected_base = None
        self.enemy_flying_dmg_units = False

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        if not local_controller.pools.ready:
            return False

        if local_controller.known_enemy_units.flying:
            if [au for au in local_controller.known_enemy_units.flying if au.can_attack_ground]:
                self.enemy_flying_dmg_units = True

        base = local_controller.townhalls.ready
        spores = local_controller.spores

        if (not len(spores) < len(base)) or local_controller.close_enemies_to_base:
            return False

        self.selected_base = base.random
        return (
            (self.enemy_flying_dmg_units or local_controller.time >= 420)
            and not local_controller.already_pending(SPORECRAWLER)
            and not spores.closer_than(15, self.selected_base.position)
            and local_controller.can_afford(SPORECRAWLER)
        )

    async def handle(self, iteration):
        """Build the spore right on the middle of the base"""
        local_controller = self.ai
        state = local_controller.state
        for base in local_controller.townhalls:
            spore_position = (state.mineral_field | state.vespene_geyser).closer_than(10, base).center.towards(base, 1)
            if not local_controller.spores.closer_than(15, spore_position):
                await local_controller.build(SPORECRAWLER, spore_position)
                return True
