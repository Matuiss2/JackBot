"""Everything related to building logic for the hives goes here"""
from sc2.constants import CANCEL_MORPHHIVE, HIVE, UPGRADETOHIVE_HIVE


class BuildHive:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.lairs = None

    async def should_handle(self, iteration):
        """Builds the hive"""
        local_controller = self.ai
        return (
            not local_controller.hives
            and local_controller.pits.ready
            and local_controller.lairs.ready.idle
            and local_controller.can_afford(HIVE)
            and not await self.morphing_lairs()
        )

    async def handle(self, iteration):
        """Finishes the action of making the hive"""
        local_controller = self.ai
        local_controller.add_action(local_controller.lairs.ready.first(UPGRADETOHIVE_HIVE))
        return True

    async def morphing_lairs(self):
        """Check if there is a lair morphing looping all hatcheries"""
        local_controller = self.ai
        for hatch in local_controller.lairs:
            if await local_controller.is_morphing(hatch, CANCEL_MORPHHIVE):
                return True
        return False
