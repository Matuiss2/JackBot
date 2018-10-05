"""SC2 zerg bot by Helfull, Matuiss, Thommath and Tweakimp"""
import sc2
from sc2.constants import (
    BARRACKS,
    CREEPTUMOR,
    CREEPTUMORBURROWED,
    CREEPTUMORQUEEN,
    DRONE,
    EVOLUTIONCHAMBER,
    GATEWAY,
    INFESTATIONPIT,
    OVERSEER,
    PHOTONCANNON,
    PROBE,
    QUEEN,
    SCV,
    SPAWNINGPOOL,
    SPINECRAWLER,
    ULTRALISK,
    ULTRALISKCAVERN,
    ZERGLING,
)

from army import ArmyControl
from buildings import Builder
from creep_spread import CreepControl
from general import ExtraThings
from production import ProductionControl
from upgrades import UpgradesControl
from worker import WorkerControl
from micro import Micro


# noinspection PyMissingConstructor
class EarlyAggro(
    sc2.BotAI, Micro, ArmyControl, WorkerControl, CreepControl, UpgradesControl, Builder, ProductionControl, ExtraThings
):
    """It makes periodic attacks with good surrounding and targeting micro, it goes ultras end-game"""

    def __init__(self):
        WorkerControl.__init__(self)
        Builder.__init__(self)
        CreepControl.__init__(self)
        ExtraThings.__init__(self)
        ArmyControl.__init__(self)
        self.close_enemies_to_base = False
        self.close_enemy_production = False
        self.actions = []
        self.locations = []
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
        """Calls used units here, so it just calls it once per loop"""
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

        if iteration == 0:  # Initialize some "global" variables
            self._client.game_step = 4  # actions every 4 frames-(optimizing so we can get it to 1 is ideal)
            self.locations = list(self.expansion_locations.keys())
            self.prepare_expansions()
            # self.send_first_overlord() # has to be after prepare_expansions
            #  since the counter for one base play is not yet implemented Ill comment it out
            # self.actions.append(self.units(OVERLORD).first.move(self._game_info.map_center))
            await self.split_workers()
        if self.known_enemy_units.not_structure.not_flying:
            for hatch in self.townhalls:
                close_enemy = self.known_enemy_units.not_structure.not_flying.closer_than(40, hatch.position)
                enemies = close_enemy.exclude_type({DRONE, SCV, PROBE})
                if enemies:
                    self.close_enemies_to_base = True
                    break
        if self.known_enemy_structures.of_type({BARRACKS, GATEWAY, PHOTONCANNON}).closer_than(50, self.start_location):
            self.close_enemy_production = True
        if iteration % 20 == 0:
            await self.all_buildings()
            await self.all_upgrades()
        if iteration % 2000 == 400:
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
