"""Everything related to building logic for the spores goes here"""
from sc2.constants import SPORECRAWLER


class BuildSpores:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.spores = None

    async def should_handle(self):
        """Requirements build the spores"""
        self.spores = self.main.spores
        spore_building_trigger = (
            self.main.flying_enemies
            and not (len(self.spores) > self.main.ready_base_amount or self.main.close_enemies_to_base)
            and (au for au in self.main.flying_enemies if au.can_attack_ground)
        )
        if self.main.ready_bases:
            return (
                (spore_building_trigger or self.main.time >= 420)
                and not self.main.already_pending(SPORECRAWLER)
                and not self.spores.closer_than(15, self.main.ready_bases.random)
                and self.main.building_requirement(SPORECRAWLER, self.main.pools.ready)
            )

    async def handle(self):
        """Build the spore right on the middle of the base"""
        state = self.main.state
        for base in self.main.ready_bases:
            spore_position = (state.mineral_field | state.vespene_geyser).closer_than(10, base).center.towards(base, 1)
            selected_drone = self.main.select_build_worker(spore_position)
            if (
                not self.main.ground_enemies.closer_than(20, spore_position)
                and selected_drone
                and not self.spores.closer_than(15, spore_position)
            ):
                build = self.main.add_action(selected_drone.build(SPORECRAWLER, spore_position))
                if not build:
                    return False
                return True
