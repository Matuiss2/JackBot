"""Upgrading hydras speed"""
from sc2.constants import RESEARCH_MUSCULARAUGMENTS, EVOLVEMUSCULARAUGMENTS, EVOLVEGROOVEDSPINES


class UpgradeMuscularAugments:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.selected_dens = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.selected_dens = local_controller.hydradens.ready.noqueue.idle
        return (
            local_controller.can_upgrade(EVOLVEMUSCULARAUGMENTS, RESEARCH_MUSCULARAUGMENTS, self.selected_dens)
            and not local_controller.floating_buildings_bm
            and local_controller.already_pending_upgrade(EVOLVEGROOVEDSPINES) == 1
        )

    async def handle(self):
        """Execute the action of upgrading hydras speed"""
        self.controller.add_action(self.selected_dens.first(RESEARCH_MUSCULARAUGMENTS))
        return True
