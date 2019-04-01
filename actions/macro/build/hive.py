"""Everything related to building logic for the hives goes here"""
from sc2.constants import AbilityId, UnitTypeId


class BuildHive:
    """Maybe can be improved"""

    def __init__(self, main):
        self.main = main
        self.selected_lairs = None

    async def should_handle(self):
        """Requirement to build the hive, maybe its too greedy maybe we should raise the lock for it"""
        self.selected_lairs = self.main.lairs.ready.idle
        return self.selected_lairs and self.main.can_build_unique(
            UnitTypeId.HIVE, self.main.caverns, self.main.pits.ready, all_units=True
        )

    async def handle(self):
        """Finishes the action of making the hive"""
        self.main.add_action(self.selected_lairs.first(AbilityId.UPGRADETOHIVE_HIVE))
