"""Everything related to building logic for the hives goes here"""
from sc2.constants import AbilityId, UnitTypeId


class TransformationToHive:
    """Maybe can be improved"""

    def __init__(self, main):
        self.main = main
        self.idle_lairs = None

    async def should_handle(self):
        """Requirement to build the hive, maybe its too greedy maybe we should raise the lock for it"""
        self.idle_lairs = self.main.lairs.ready.idle
        return self.idle_lairs and self.main.can_build_unique(
            UnitTypeId.HIVE, self.main.caverns, self.main.pits.ready
        )

    async def handle(self):
        """Finishes the action of making the hive"""
        self.main.add_action(self.idle_lairs.first(AbilityId.UPGRADETOHIVE_HIVE))
