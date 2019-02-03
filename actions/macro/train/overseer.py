"""Everything related to training overseers goes here"""
from sc2.constants import MORPH_OVERSEER, OVERLORDCOCOON, OVERSEER


class TrainOverseer:
    """Should be expanded a little, it needs at least one more to run alongside the offensive army"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to morph overseers"""
        return (
            (self.controller.lairs or self.controller.hives)
            and self.controller.overlords
            and not self.controller.already_pending(OVERSEER, all_units=True)
            and self.controller.can_afford(OVERSEER)
            and len(self.controller.overseers) < len(self.controller.townhalls.ready)
        )

    async def handle(self):
        """Morph the overseer"""
        selected_ov = self.controller.overlords.random
        overseers = self.controller.overseers | self.controller.units(OVERLORDCOCOON)
        if overseers:
            if selected_ov.distance_to(overseers.closest_to(selected_ov)) > 10:
                self.controller.actions.append(selected_ov(MORPH_OVERSEER))
        else:
            self.controller.actions.append(selected_ov(MORPH_OVERSEER))
