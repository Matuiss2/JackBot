"""Everything related to building logic for the hives goes here"""
from sc2.constants import HIVE, UPGRADETOHIVE_HIVE


class BuildHive:
    """Maybe can be improved"""

    def __init__(self, main):
        self.controller = main
        self.selected_lairs = None

    async def should_handle(self):
        """Requirement to build the hive, maybe its too greedy maybe we should raise the lock for it"""
        self.selected_lairs = self.controller.lairs.ready.idle
        return self.selected_lairs and self.controller.can_build_unique(
            HIVE, self.controller.caverns, self.controller.pits.ready, all_units=True
        )

    async def handle(self):
        """Finishes the action of making the hive"""
        self.controller.add_action(self.selected_lairs.first(UPGRADETOHIVE_HIVE))
        return True
