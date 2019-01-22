"""Everything related to training hydralisks goes here"""
from sc2.constants import HIVE, HYDRALISK


class TrainHydralisk:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main

    async def should_handle(self):
        """Requirements to run handle, it limits the training a little so it keeps building ultralisks,
         needs more limitations so the transition to hive is smoother"""
        local_controller = self.controller
        cavern = local_controller.caverns
        if local_controller.hives and not cavern:
            return False
        if not local_controller.can_train(HYDRALISK, local_controller.hydradens.ready):
            return False
        if (
            local_controller.pits.ready
            and not local_controller.hives
            and not local_controller.already_pending(HIVE, all_units=True)
        ):
            return False
        if cavern.ready:
            return len(local_controller.ultralisks) * 3.5 > len(local_controller.hydras)
        return not local_controller.floating_buildings_bm

    async def handle(self):
        """Execute the action of training hydras"""
        local_controller = self.controller
        local_controller.add_action(local_controller.larvae.random.train(HYDRALISK))
        return True
