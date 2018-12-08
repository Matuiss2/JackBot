"""Everything related to building logic for the infestation pits goes here"""
from sc2.constants import INFESTATIONPIT, ZERGGROUNDARMORSLEVEL2


class BuildPit:
    """Ok for now"""

    def __init__(self, ai):
        self.controller = ai

    async def should_handle(self):
        """Builds the infestation pit, placement fails on very limited situations"""
        local_controller = self.controller
        return (
            len(local_controller.townhalls) > 4
            and local_controller.already_pending_upgrade(ZERGGROUNDARMORSLEVEL2)
            and local_controller.can_build_unique(INFESTATIONPIT, local_controller.pits)
        )

    async def handle(self):
        """Build it behind the mineral line if there is space, if not uses later placement"""
        local_controller = self.controller
        position = await local_controller.get_production_position()
        if position:
            await local_controller.build(INFESTATIONPIT, position)
            return True
        await local_controller.build(INFESTATIONPIT, near=self.hardcoded_position())
        return True

    def hardcoded_position(self):
        """Previous placement"""
        local_controller = self.controller
        return local_controller.furthest_townhall_to_map_center.position.towards_with_random_angle(
            local_controller.game_info.map_center, -14
        )
