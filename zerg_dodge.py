from s2clientprotocol import debug_pb2 as debug_pb
"""SC2 zerg bot by Matuiss, Thommath and Tweakimp"""
import sc2
from sc2.units import Units
from sc2.constants import (
    ZERGLING,
    SIEGETANK,
    SIEGETANKSIEGED,
    ADEPTPHASESHIFT,
    DISRUPTORPHASED,
    EGG,
    LARVA,
    INFESTEDTERRANSEGG,
    INFESTEDTERRAN,
    AUTOTURRET,
    SPINECRAWLER,
    PHOTONCANNON,
    BUNKER,
    PLANETARYFORTRESS,
    ZERGLINGATTACKSPEED,
    ULTRALISK
)

# noinspection PyMissingConstructor
class EarlyAggro(
    sc2.BotAI
):
    def __init__(self):
        self.actions = []
        self.zerglings = None
        self.ultralisks = None
        self.current_zerglings = []
        self.ft = None
        self.SPLIT_RANGE = 2

    async def on_step(self, iteration):
        self.ultralisks = self.units(ULTRALISK)
        self.zerglings = self.units(ZERGLING)
        self.actions = []

        await self.just_attack()
        await self.split_closest()
        await self._client.send_debug()
        await self.do_actions(self.actions)

    async def just_attack(self):
        for unit in self.units:
            self.actions.append(unit.attack(self.known_enemy_units.closest_to(unit)))

    async def split_closest(self):
        self.SPLIT_RANGE = 3
        sieged_tanks = self.known_enemy_units.of_type([SIEGETANK, SIEGETANKSIEGED])
        if len(sieged_tanks) == 0:
            return

        for enemy in sieged_tanks:

            if len(self.zerglings) < 5:
                continue

            closest_lings = Units(self.zerglings.sorted_by_distance_to(enemy).take(3), self._game_data)

            for cling in closest_lings:
                self.actions.append(cling.attack(enemy))

            other_lings = self.zerglings.tags_not_in(closest_lings.tags)
            for ling in other_lings:
                lings = other_lings.tags_not_in([ling.tag])

                if (
                    not ling.target_in_range(enemy)
                    and enemy.ground_range + 5 > ling.distance_to(enemy)
                    and len(lings.closer_than(self.SPLIT_RANGE, ling)) > 0
                ):
                    closest_ling = lings.closest_to(ling)
                    self.actions.append(ling.move(ling.position.towards(closest_ling.position, -self.SPLIT_RANGE, True)))
                else:
                    self.actions.append(ling.attack(enemy))
