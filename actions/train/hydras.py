"""Everything related to training mutalisks goes here"""
from sc2.constants import HYDRALISK


class TrainHydralisk:
    """Untested"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        if local_controller.caverns.ready:
            if not len(local_controller.ultralisks) * 2.75 > len(local_controller.hydras):
                return False
        return (
            local_controller.hydradens.ready
            and not local_controller.floating_buildings_bm
            and local_controller.can_train(HYDRALISK)
        )

    async def handle(self, iteration):
        """Execute the action of training mutas"""
        local_controller = self.ai
        local_controller.add_action(local_controller.larvae.random.train(HYDRALISK))
        return True
