"""Everything related to training overseers goes here"""
from sc2.constants import AbilityId, UnitTypeId


class OverseerCreation:
    """Should be expanded a little, it needs at least one more to run alongside the offensive army"""

    def __init__(self, main):
        self.main = main
        self.overseers = self.selected_ov = None

    async def should_handle(self):
        """Requirements to morph overseers"""
        self.overseers = self.main.overseers | self.main.units(UnitTypeId.OVERLORDCOCOON)
        self.selected_ov = self.main.overlords.random
        return (
            self.main.building_requirement(UnitTypeId.OVERSEER, (self.main.lairs or self.main.hives), one_at_time=True)
            and self.main.overlords
            and len(self.main.overseers) < self.main.ready_base_amount
            and (not self.overseers or self.selected_ov.distance_to(self.overseers.closest_to(self.selected_ov)) > 10)
        )

    async def handle(self):
        """Morph the overseer"""
        self.main.add_action(self.selected_ov(AbilityId.MORPH_OVERSEER))
