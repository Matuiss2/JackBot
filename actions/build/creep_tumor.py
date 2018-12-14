"""Everything related to placing creep tumors goes here"""


class CreepTumor:
    """Ok for now"""

    def __init__(self, main):
        self.controller = main
        self.tumors = None

    async def should_handle(self):
        """Requirements to run handle"""
        local_controller = self.controller
        self.tumors = local_controller.tumors.tags_not_in(local_controller.used_tumors)
        return self.tumors

    async def handle(self):
        """Place the tumor"""
        for tumor in self.tumors:
            await self.controller.place_tumor(tumor)
