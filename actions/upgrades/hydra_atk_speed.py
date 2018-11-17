"""Upgrading hydras atk speed"""
from sc2.constants import RESEARCH_GROOVEDSPINES, EVOLVEGROOVEDSPINES


class UpgradeGroovedSpines:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return (
            local_controller.hydradens.ready.noqueue.idle
            and local_controller.can_upgrade(EVOLVEGROOVEDSPINES, RESEARCH_GROOVEDSPINES)
            and not local_controller.floating_buildings_bm
        )

    async def handle(self, iteration):
        """Execute the action of upgrading hydras atk speed"""
        local_controller = self.ai
        local_controller.add_action(local_controller.hydradens.noqueue.first(RESEARCH_GROOVEDSPINES))
        return True
