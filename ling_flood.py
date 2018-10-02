"""SC2 zerg bot by Matuiss, Thommath and Tweakimp"""
import sc2
from sc2 import Difficulty, Race
from sc2.constants import (
    BARRACKS,
    GATEWAY,
    CREEPTUMOR,
    CREEPTUMORBURROWED,
    CREEPTUMORQUEEN,
    DRONE,
    EVOLUTIONCHAMBER,
    INFESTATIONPIT,
    OVERLORD,
    OVERSEER,
    PHOTONCANNON,
    PROBE,
    QUEEN,
    RESEARCH_ZERGGROUNDARMORLEVEL1,
    RESEARCH_ZERGGROUNDARMORLEVEL2,
    RESEARCH_ZERGGROUNDARMORLEVEL3,
    RESEARCH_ZERGMELEEWEAPONSLEVEL1,
    RESEARCH_ZERGMELEEWEAPONSLEVEL2,
    RESEARCH_ZERGMELEEWEAPONSLEVEL3,
    SCV,
    SPAWNINGPOOL,
    SPINECRAWLER,
    ZERGLING,
    QUEEN,
    ULTRALISK,
    ULTRALISKCAVERN,
)
from sc2.player import Bot, Computer

from army import army_control
from buildings import builder
from creep_spread import creep_control
from general import extra_things
from production import production_control
from upgrades import upgrades_control
from worker import worker_control


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
        army_control.__init__(self)
        self.close_enemies_to_base = False
        self.close_enemy_production = False
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
        self.drones = None
        self.queens = None
        self.zerglings = None
        self.ultralisks = None
        self.overseers = None
        self.evochambers = None
        self.caverns = None
        self.pools = None
        self.pits = None
        self.spines = None
        self.tumors = None
        self.retreat_units = set()

    async def on_step(self, iteration):
        self.drones = self.units(DRONE)
        self.queens = self.units(QUEEN)
        self.zerglings = self.units(ZERGLING)
        self.ultralisks = self.units(ULTRALISK)
        self.overseers = self.units(OVERSEER)
        self.evochambers = self.units(EVOLUTIONCHAMBER)
        self.caverns = self.units(ULTRALISKCAVERN)
        self.pools = self.units(SPAWNINGPOOL)
        self.pits = self.units(INFESTATIONPIT)
        self.spines = self.units(SPINECRAWLER)
        self.actions = []
        self.close_enemies_to_base = False
        self.close_enemy_production = False
        self.tumors = self.units(CREEPTUMORQUEEN) | self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED)

        if iteration == 0:
            self._client.game_step = 4
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
        if self.known_enemy_structures.of_type({BARRACKS, GATEWAY, PHOTONCANNON}).closer_than(50, self.start_location):
            self.close_enemy_production = True
        if iteration % 20 == 0:
            await self.all_buildings()
            await self.all_upgrades()
        if iteration % 3000 == 400:
            self.scout_map()
        self.army_micro()
        await self.build_units()
        self.cancel_attacked_hatcheries()
        await self.defend_worker_rush()
        await self.detection()
        self.detection_control()
        await self.distribute_drones()
        await self.morphing_townhalls()
        await self.queens_abilities()
        await self.spread_creep()
        await self.do_actions(self.actions)
