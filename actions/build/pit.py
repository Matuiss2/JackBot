"""Everything related to building logic for the infestation pits goes here"""
from sc2.constants import INFESTATIONPIT, ZERGGROUNDARMORSLEVEL2


class BuildPit:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Builds the infestation pit, placement can maybe be improved(far from priority)"""
        local_controller = self.ai
        base = local_controller.townhalls
        return (
            (not len(base) < 4)
            and local_controller.evochambers
            and local_controller.lairs.ready
            and local_controller.already_pending_upgrade(ZERGGROUNDARMORSLEVEL2) > 0
            and local_controller.can_build_uniques(INFESTATIONPIT, local_controller.pits)
            and base
            and local_controller.hydradens.ready
        )

    async def handle(self, iteration):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        local_controller = self.ai
        map_center = local_controller.game_info.map_center
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(INFESTATIONPIT, position)
            return True
        await local_controller.build(
            INFESTATIONPIT,
            near=local_controller.townhalls.furthest_to(map_center).position.towards_with_random_angle(map_center, -14),
        )
        return True
