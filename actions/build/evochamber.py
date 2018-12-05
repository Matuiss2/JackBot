"""Everything related to building logic for the evolution chamber goes here"""
from sc2.constants import EVOLUTIONCHAMBER


class BuildEvochamber:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Builds the evolution chambers"""
        local_controller = self.ai
        return (
            local_controller.pools.ready
            and local_controller.can_afford(EVOLUTIONCHAMBER)
            and (
                len(local_controller.townhalls) >= 3
                or (local_controller.close_enemy_production and len(local_controller.spines.ready) >= 4)
            )
            and len(local_controller.evochambers) + local_controller.already_pending(EVOLUTIONCHAMBER) < 2
        )

    async def handle(self, iteration):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        local_controller = self.ai
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(EVOLUTIONCHAMBER, position)
            return True
        await local_controller.build(
            EVOLUTIONCHAMBER,
            local_controller.townhalls.random.position.towards_with_random_angle(
                local_controller.game_info.map_center, -14
            ),
        )
        return True
