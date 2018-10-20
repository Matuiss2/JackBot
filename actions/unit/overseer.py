"""Everything related to controlling overseers goes here"""


class Overseer:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        return self.ai.overseers and (self.ai.zerglings | self.ai.ultralisks or self.ai.townhalls)

    async def handle(self, iteration):
        """It sends the overseer at the closest ally, can be improved a lot"""
        atk_force = self.ai.zerglings | self.ai.ultralisks
        action = self.ai.add_action
        selected_ov = self.ai.overseers.first
        move_overseer = selected_ov.move
        overseer_position = selected_ov.position
        if atk_force:
            action(move_overseer(atk_force.closest_to(overseer_position)))
        elif self.ai.townhalls:
            action(move_overseer(self.ai.townhalls.closest_to(overseer_position)))
