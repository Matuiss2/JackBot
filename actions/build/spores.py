"""Everything related to building logic for the spores goes here"""
from sc2.constants import SPORECRAWLER


class BuildSpores:
    """Ok for now"""

    def __init__(self, ai):
        self.controller = ai
        self.selected_base = None
        self.spore_building_trigger = False

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        base = local_controller.townhalls.ready
        spores = local_controller.spores
        self.spore_building_trigger = (
            local_controller.flying_enemies
            and not (len(spores) > len(base) or local_controller.close_enemies_to_base)
            and (au for au in local_controller.flying_enemies if au.can_attack_ground)
        )
        if base:
            return (
                (self.spore_building_trigger or local_controller.time >= 420)
                and not local_controller.already_pending(SPORECRAWLER)
                and not spores.closer_than(15, base.random)
                and local_controller.building_requirement(SPORECRAWLER, local_controller.pools.ready)
            )

    async def handle(self):
        """Build the spore right on the middle of the base, sometimes it fails"""
        local_controller = self.controller
        state = local_controller.state
        for base in local_controller.townhalls.ready:
            spore_position = (state.mineral_field | state.vespene_geyser).closer_than(10, base).center.towards(base, 1)
            if not local_controller.spores.closer_than(15, spore_position):
                await local_controller.build(SPORECRAWLER, spore_position)
                return True
