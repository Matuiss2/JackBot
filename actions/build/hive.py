"""Everything related to building logic for the hives goes here"""
from sc2.constants import CANCEL_MORPHHIVE, HIVE, UPGRADETOHIVE_HIVE


class BuildHive:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.selected_lairs = None

    async def should_handle(self):
        """Builds the hive"""
        local_controller = self.ai
        self.selected_lairs = local_controller.lairs.ready.idle
        return (
            self.selected_lairs
            and local_controller.can_build_unique(HIVE, local_controller.caverns, local_controller.pits.ready)
            and not await self.morphing_lairs()
        )

    async def handle(self):
        """Finishes the action of making the hive"""
        local_controller = self.ai
        local_controller.add_action(self.selected_lairs.first(UPGRADETOHIVE_HIVE))
        return True

    async def morphing_lairs(self):
        """Check if there is a lair morphing looping all hatcheries"""
        local_controller = self.ai
        for hatch in local_controller.lairs:
            if await local_controller.is_morphing(hatch, CANCEL_MORPHHIVE):
                return True
        return False
