"""Everything related to building logic for the evolution chamber goes here"""
from sc2.constants import EVOLUTIONCHAMBER


class BuildEvochamber:
    """Ok for now"""

    def __init__(self, ai):
        self.controller = ai

    async def should_handle(self):
        """Builds the evolution chambers"""
        local_controller = self.controller
        return (
            local_controller.building_requirement(EVOLUTIONCHAMBER, local_controller.pools.ready)
            and (
                len(local_controller.townhalls) >= 3
                or (local_controller.close_enemy_production and len(local_controller.spines.ready) >= 4)
            )
            and len(local_controller.evochambers) + local_controller.already_pending(EVOLUTIONCHAMBER) < 2
        )

    async def handle(self):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(EVOLUTIONCHAMBER, position)
            return True
        if local_controller.townhalls:
            await local_controller.build(EVOLUTIONCHAMBER, self.hardcoded_position())
            return True

    def hardcoded_position(self):
        """Previous placement"""
        local_controller = self.controller
        return local_controller.furthest_townhall_to_map_center.position.towards_with_random_angle(
            local_controller.game_info.map_center, -14
        )
