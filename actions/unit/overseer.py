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

        selected_ov = self.ai.overseers.first
        if atk_force:
            self.ai.actions.append(selected_ov.move(atk_force.closest_to(selected_ov.position)))
        elif self.ai.townhalls:
            self.ai.actions.append(selected_ov.move(self.ai.townhalls.closest_to(selected_ov.position)))
