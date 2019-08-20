"""Everything related to training overseers goes here"""
from sc2.constants import AbilityId, UnitTypeId


class OverseerCreation:
    """Should be expanded a little, it needs at least one more to run alongside the offensive army"""

    def __init__(self, main):
        self.main = main
        self.random_ov = None

    async def should_handle(self):
        """Requirements to morph overseers"""
        overseers = self.main.overseers | self.main.units(UnitTypeId.OVERLORDCOCOON)  # to save lines
        if self.main.overlords:
            self.random_ov = self.main.overlords.random
            return (
                self.main.building_requirement(UnitTypeId.OVERSEER, self.main.upgraded_bases, one_at_time=True)
                and len(self.main.overseers) < self.main.ready_base_amount
                and (not overseers or self.random_ov.distance_to(overseers.closest_to(self.random_ov)) > 10)
            )

    async def handle(self):
        """Morph the overseer"""
        self.main.add_action(self.random_ov(AbilityId.MORPH_OVERSEER))
