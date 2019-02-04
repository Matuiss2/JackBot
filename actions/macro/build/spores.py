"""Everything related to building logic for the spores goes here"""
from sc2.constants import SPORECRAWLER


class BuildSpores:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.spores = self.base = None

    async def should_handle(self):
        """Requirements build the spores"""
        self.base = self.controller.townhalls.ready
        self.spores = self.controller.spores
        spore_building_trigger = (
            self.controller.flying_enemies
            and not (len(self.spores) > len(self.base) or self.controller.close_enemies_to_base)
            and (au for au in self.controller.flying_enemies if au.can_attack_ground)
        )
        if self.base:
            return (
                (spore_building_trigger or self.controller.time >= 420)
                and not self.controller.already_pending(SPORECRAWLER)
                and not self.spores.closer_than(15, self.base.random)
                and self.controller.building_requirement(SPORECRAWLER, self.controller.pools.ready)
            )

    async def handle(self):
        """Build the spore right on the middle of the base"""
        state = self.controller.state
        for base in self.base:
            spore_position = (state.mineral_field | state.vespene_geyser).closer_than(10, base).center.towards(base, 1)
            selected_drone = self.controller.select_build_worker(spore_position)
            if (
                not self.controller.ground_enemies.closer_than(20, spore_position)
                and selected_drone
                and not self.spores.closer_than(15, spore_position)
            ):
                build = self.controller.add_action(selected_drone.build(SPORECRAWLER, spore_position))
                if not build:
                    return False
                return True
