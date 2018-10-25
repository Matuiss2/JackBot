"""Everything related to controlling overseers goes here"""


class Overseer:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        return local_controller.overseers and (
            local_controller.zerglings | local_controller.ultralisks or local_controller.townhalls
        )

    async def handle(self, iteration):
        """It sends the overseer at the closest ally, can be improved a lot"""
        local_controller = self.ai
        bases = local_controller.townhalls
        atk_force = local_controller.zerglings | local_controller.ultralisks
        action = local_controller.add_action
        selected_ov = local_controller.overseers.first
        move_overseer = selected_ov.move
        overseer_position = selected_ov.position
        if atk_force:
            action(move_overseer(atk_force.closest_to(overseer_position)))
        elif bases:
            action(move_overseer(bases.closest_to(overseer_position)))
