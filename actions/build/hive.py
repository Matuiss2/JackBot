"""Everything related to building logic for the hives goes here"""
from sc2.constants import CANCEL_MORPHHIVE, HIVE, UPGRADETOHIVE_HIVE


class BuildHive:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.lairs = None

    async def should_handle(self, iteration):
        """Builds the infestation pit, placement can maybe be improved(far from priority)"""
        local_controller = self.ai
        if local_controller.hives:
            return False

        self.lairs = local_controller.lairs.ready

        return (
            local_controller.pit.ready
            and self.lairs.idle
            and local_controller.can_afford(HIVE)
            and not await self.morphing_lairs()
        )

    async def handle(self, iteration):
        """Finishes the action of making the hive"""
        self.ai.add_action(self.lairs.ready.first(UPGRADETOHIVE_HIVE))
        return True

    async def morphing_lairs(self):
        """Check if there is a lair morphing looping all hatcheries"""
        for hatch in self.lairs:
            if await self.is_morphing(hatch):
                return True
        return False

    async def is_morphing(self, hatch):
        """Check if there is a lair morphing by checking the available abilities"""
        abilities = await self.ai.get_available_abilities(hatch)
        return CANCEL_MORPHHIVE in abilities
