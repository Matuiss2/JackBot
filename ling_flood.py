"""SC2 zerg bot by Matuiss, Thommath and Tweakimp"""
import sc2
from sc2.player import Bot, Computer
from sc2 import Difficulty, Race, maps, run_game
from sc2.constants import (
    DRONE,
    OVERLORD,
    OVERSEER,
    PROBE,
    RESEARCH_ZERGGROUNDARMORLEVEL1,
    RESEARCH_ZERGGROUNDARMORLEVEL2,
    RESEARCH_ZERGGROUNDARMORLEVEL3,
    RESEARCH_ZERGMELEEWEAPONSLEVEL1,
    RESEARCH_ZERGMELEEWEAPONSLEVEL2,
    RESEARCH_ZERGMELEEWEAPONSLEVEL3,
    SCV,
)

from army import army_control
from worker import worker_control
from creep_spread import creep_control
from upgrades import upgrades_control
from buildings import builder
from production import production_control
from general import extra_things

# noinspection PyMissingConstructor
class EarlyAggro(
    sc2.BotAI, army_control, worker_control, creep_control, upgrades_control, builder, production_control, extra_things
):
    """It makes one attack early then tried to make a very greedy transition"""

    def __init__(self):
        worker_control.__init__(self)
        builder.__init__(self)
        creep_control.__init__(self)
        extra_things.__init__(self)
        self.close_enemies_to_base = False
        self.actions = []
        self.locations = []
        self.abilities_list = {
            RESEARCH_ZERGMELEEWEAPONSLEVEL1,
            RESEARCH_ZERGGROUNDARMORLEVEL1,
            RESEARCH_ZERGMELEEWEAPONSLEVEL2,
            RESEARCH_ZERGGROUNDARMORLEVEL2,
            RESEARCH_ZERGMELEEWEAPONSLEVEL3,
            RESEARCH_ZERGGROUNDARMORLEVEL3,
        }


    async def on_step(self, iteration):
        self.actions = []
        self.close_enemies_to_base = False
        if iteration == 0:
            self.actions.append(self.units(OVERLORD).first.move(self._game_info.map_center))
            self.locations = list(self.expansion_locations.keys())
            await self.split_workers()
        if self.known_enemy_units.not_structure.not_flying:  # I only go to the loop if possibly needed
            for hatch in self.townhalls:
                close_enemy = self.known_enemy_units.not_structure.closer_than(40, hatch.position)
                enemies = close_enemy.exclude_type({DRONE, SCV, PROBE})
                if enemies:
                    self.close_enemies_to_base = True
                    break
        if iteration % 10 == 0:
            await self.all_buildings()
            await self.all_upgrades()
        self.army_micro()
        await self.build_units()
        self.cancel_attacked_hatcheries()
        await self.defend_worker_rush()
        await self.detection()
        await self.distribute_drones()
        self.finding_bases()
        await self.morphing_townhalls()
        await self.queens_abilities()
        await self.spread_creep()
        await self.do_actions(self.actions)

for it in range(1):
    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EarlyAggro()), Computer(Race.Protoss, Difficulty.CheatVision)],
        realtime=False,
    )

    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EarlyAggro()), Computer(Race.Zerg, Difficulty.CheatVision)],
        realtime=False,
    )

    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EarlyAggro()), Computer(Race.Terran, Difficulty.CheatVision)],
        realtime=False,
    )

run_game(
    maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EarlyAggro()), Computer(Race.Protoss, Difficulty.Hard)], realtime=False
)

# better detection mid game(probably use changelings)
# v1 vs ladder 1234 ELO
# 194-37 rework
