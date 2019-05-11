"""Everything related to placing creep tumors using tumors goes here"""


class CreepTumor:
    """Ok for now"""

    def __init__(self, main):
        self.main = main
        self.tumors = None

    async def should_handle(self):
        """Requirements to run handle"""
        self.tumors = self.main.tumors.tags_not_in(self.main.used_tumors)
        return self.tumors

    async def handle(self):
        """Place the tumor"""
        for tumor in self.tumors:
            await self.main.place_tumor(tumor)
