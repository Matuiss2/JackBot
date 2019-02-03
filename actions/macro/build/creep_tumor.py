"""Everything related to placing creep tumors goes here(maybe merging with creep_spread would be good)"""


class CreepTumor:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.tumors = None

    async def should_handle(self):
        """Requirements to run handle"""
        self.tumors = self.controller.tumors.tags_not_in(self.controller.used_tumors)
        return self.tumors

    async def handle(self):
        """Place the tumor"""
        for tumor in self.tumors:
            await self.controller.place_tumor(tumor)
