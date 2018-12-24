"""Run the ladder or local game"""
import random
import sys
import sc2
from sc2 import DIFFICULTY, RACE
from sc2.player import Bot, Computer
from __init__ import run_ladder_game
from main import JackBot

BOT = Bot(RACE.Zerg, JackBot())
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        run_ladder_game(BOT)
    else:
        # Local game
        print("Starting local game...")
        RANDOM_MAP = random.choice(
            ["AcidPlantLE", "BlueshiftLE", "CeruleanFallLE", "DreamcatcherLE", "FractureLE", "LostAndFoundLE"]
        )

        sc2.run_game(sc2.maps.get(RANDOM_MAP), [BOT, Computer(RACE.Zerg, DIFFICULTY.CheatVision)], realtime=False)
        # sc2.run_game(sc2.maps.get("drone_worker_defense"), [bot], realtime=True)
        # sc2.run_game(sc2.maps.get("drone_scout_defense"), [bot], realtime=True)
        # sc2.run_game(sc2.maps.get("test_anti_colossus"),[bot, Computer(Race.Protoss,
        #                                                    Difficulty.CheatInsane)],realtime=True)
