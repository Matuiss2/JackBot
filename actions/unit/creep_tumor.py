"""Everything related to placing creep tumors goes here"""


class CreepTumor:
    """Ok for now"""

    def __init__(self, ai):
        self.ai = ai
        self.tumors = None

    async def should_handle(self, iteration):
        """Requirements to run handle"""
        self.tumors = self.ai.tumors.tags_not_in(self.ai.used_tumors)
        return self.tumors

    async def handle(self, iteration):
        """Place the tumor"""
        for tumor in self.tumors:
            await self.ai.place_tumor(tumor)
