"""Everything related to scouting with changelings goes here"""


class ChangelingControl:
    """Ok for now"""

    def __init__(self, main):
        self.main = main

    async def should_handle(self):
        """Sends the scouting drone changelings when not playing against proxies"""
        return not self.main.close_enemy_production

    async def handle(self):
        """It sends all changelings to scout the bases periodically"""
        for changeling in self.main.changelings:
            for point in self.main.ordered_expansions[self.main.ready_base_amount :]:
                self.main.add_action(changeling.move(point, queue=True))
