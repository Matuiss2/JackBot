"""Everything related to building logic for the spores goes here"""
from sc2.constants import SPORECRAWLER


class BuildSpores:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements build the spores"""
        local_controller = self.controller
        base = local_controller.townhalls.ready
        spores = local_controller.spores
        spore_building_trigger = (
            local_controller.flying_enemies
            and not (len(spores) > len(base) or local_controller.close_enemies_to_base)
            and (au for au in local_controller.flying_enemies if au.can_attack_ground)
        )
        if base:
            return (
                (spore_building_trigger or local_controller.time >= 420)
                and not local_controller.already_pending(SPORECRAWLER)
                and not spores.closer_than(15, base.random)
                and local_controller.building_requirement(SPORECRAWLER, local_controller.pools.ready)
            )

    async def handle(self):
        """Build the spore right on the middle of the base"""
        local_controller = self.controller
        state = local_controller.state
        for base in local_controller.townhalls.ready:
            spore_position = (state.mineral_field | state.vespene_geyser).closer_than(10, base).center.towards(base, 1)
            selected_drone = local_controller.select_build_worker(spore_position)
            if (
                not local_controller.ground_enemies.closer_than(20, spore_position)
                and selected_drone
                and not local_controller.spores.closer_than(15, spore_position)
            ):
                build = local_controller.add_action(selected_drone.build(SPORECRAWLER, spore_position))
                if not build:
                    return False
                return True
