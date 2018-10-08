class Overlord:
    def __init__(self, ai):
        self.ai = ai

    async def should_handle(self, iteration):
        return self.ai.overlords and self.ai.enemy_start_locations

    async def handle(self, iteration):
        enemy_main = self.ai.enemy_start_locations[0]  # point2
        enemy_natural = min(
            self.ai.ordered_expansions,
            key=lambda expo: (expo.x - enemy_main.x) ** 2 + (expo.y - enemy_main.y) ** 2
            if expo.x - enemy_main.x != 0 and expo.y - enemy_main.y != 0
            else 10 ** 10,
        )
        self.ai.actions.append(self.ai.overlords.first.move(enemy_natural.towards(enemy_main, -11)))
