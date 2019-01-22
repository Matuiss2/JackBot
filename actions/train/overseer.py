"""Everything related to training overseers goes here"""
from sc2.constants import MORPH_OVERSEER, OVERLORDCOCOON, OVERSEER


class TrainOverseer:
    """Should be expanded"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to run handle, limits it to one it need to be expanded"""
        local_controller = self.controller
        return (
            (local_controller.lairs or local_controller.hives)
            and local_controller.overlords
            and not local_controller.already_pending(OVERSEER, all_units=True)
            and local_controller.can_afford(OVERSEER)
            and len(local_controller.overseers) < len(local_controller.townhalls.ready)
        )

    async def handle(self):
        """Morph the overseer"""
        local_controller = self.controller
        selected_ov = local_controller.overlords.random
        overseers = local_controller.overseers | local_controller.units(OVERLORDCOCOON)
        if overseers:
            if selected_ov.distance_to(overseers.closest_to(selected_ov)) > 10:
                local_controller.actions.append(selected_ov(MORPH_OVERSEER))
        else:
            local_controller.actions.append(selected_ov(MORPH_OVERSEER))
