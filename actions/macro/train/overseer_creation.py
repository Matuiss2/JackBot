"""Everything related to training overseers goes here"""
from sc2.constants import AbilityId, UnitTypeId


class OverseerCreation:
    """Should be expanded a little, it needs at least one more to run alongside the offensive army"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Requirements to morph overseers"""
        return (
            self.main.building_requirement(UnitTypeId.OVERSEER, (self.main.lairs or self.main.hives), one_at_time=True)
            and self.main.overlords
            and len(self.main.overseers) < self.main.ready_base_amount
        )

    async def handle(self):
        """Morph the overseer"""
        selected_ov = self.main.overlords.random
        overseers = self.main.overseers | self.main.units(UnitTypeId.OVERLORDCOCOON)
        if overseers:
            if selected_ov.distance_to(overseers.closest_to(selected_ov)) > 10:
                self.main.add_action(selected_ov(AbilityId.MORPH_OVERSEER))
        else:
            self.main.add_action(selected_ov(AbilityId.MORPH_OVERSEER))
