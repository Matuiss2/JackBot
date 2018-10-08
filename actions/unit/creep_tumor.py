class CreepTumor:
    def __init__(self, ai):
        self.ai = ai
        self.tumors = None

    async def should_handle(self, iteration):
        self.tumors = self.ai.tumors.tags_not_in(self.ai.used_tumors)
        return self.tumors

    async def handle(self, iteration):
        for tumor in self.tumors:
            await self.ai.place_tumor(tumor)
