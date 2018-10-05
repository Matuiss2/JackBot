import random
import sys

import sc2
from sc2 import Difficulty, Race
from sc2.player import Bot, Computer

from __init__ import run_ladder_game
from ling_flood import EarlyAggro

bot = Bot(Race.Zerg, EarlyAggro())

# Start game
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        run_ladder_game(bot)
    else:
        # Local game
        print("Starting local game...")
        random_map = random.choice(
            [
                "AcidPlantLE",
                "BlueshiftLE",
                "CeruleanFallLE",
                "DreamcatcherLE",
                "FractureLE",
                "LostAndFoundLE",
                "ParaSiteLE",
            ]
        )

        sc2.run_game(sc2.maps.get(random_map), [bot, Computer(Race.Random, Difficulty.CheatVision)], realtime=False)
        # sc2.run_game(sc2.maps.get("drone_worker_defense"), [bot], realtime=True)
        # sc2.run_game(sc2.maps.get("drone_scout_defense"), [bot], realtime=True)
        # sc2.run_game(sc2.maps.get("lings_dodge_tanks"), [bot], realtime=True)
