"""Upgrading hydras speed"""
from sc2.constants import RESEARCH_MUSCULARAUGMENTS, EVOLVEMUSCULARAUGMENTS, EVOLVEGROOVEDSPINES


class UpgradeMuscularAugments:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.selected_dens = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        self.selected_dens = local_controller.hydradens.ready.noqueue.idle
        return (
            local_controller.can_upgrade(EVOLVEMUSCULARAUGMENTS, RESEARCH_MUSCULARAUGMENTS, self.selected_dens)
            and not local_controller.floating_buildings_bm
            and local_controller.already_pending_upgrade(EVOLVEGROOVEDSPINES) == 1
        )

    async def handle(self, iteration):
        """Execute the action of upgrading hydras speed"""
        self.ai.add_action(self.selected_dens.first(RESEARCH_MUSCULARAUGMENTS))
        return True
