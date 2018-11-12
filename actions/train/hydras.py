"""Everything related to training hydralisks goes here"""
from sc2.constants import HYDRALISK


class TrainHydralisk:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle, it limits the training a little so it keeps building ultralisks,
         needs more limitations so the transition to hive is smoother"""
        local_controller = self.ai
        if local_controller.caverns.ready:
            if len(local_controller.ultralisks) * 2.75 <= len(local_controller.hydras):
                return False
        return (
            local_controller.hydradens.ready
            and not local_controller.floating_buildings_bm
            and local_controller.can_train(HYDRALISK)
        )

    async def handle(self, iteration):
        """Execute the action of training hydras"""
        local_controller = self.ai
        local_controller.add_action(local_controller.larvae.random.train(HYDRALISK))
        return True
