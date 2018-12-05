"""Everything related to placing creep tumors goes here"""


class CreepTumor:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.tumors = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        local_controller = self.ai
        self.tumors = local_controller.tumors.tags_not_in(local_controller.used_tumors)
        return self.tumors

    async def handle(self, iteration):
        """Place the tumor"""
        for tumor in self.tumors:
            await self.ai.place_tumor(tumor)
