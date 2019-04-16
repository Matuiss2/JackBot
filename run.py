"""Run the ladder or local game"""
import random
import sys
import sc2
from sc2 import Race, Difficulty  # AIBuild
from sc2.player import Bot, Computer
from __init__ import run_ladder_game
from main import JackBot

BOT = Bot(Race.Zerg, JackBot())
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        run_ladder_game(BOT)
    else:
        # Local game
        print("Starting local game...")
        RANDOM_MAP = random.choice(("BlueshiftLE", "KairosJunctionLE", "ParaSiteLE", "PortAleksanderLE"))
        # RANDOM_BUILD = random.choice(
        # (sc2.AIBuild.Rush, sc2.AIBuild.Timing, sc2.AIBuild.Power, sc2.AIBuild.Macro, sc2.AIBuild.Air)
        # )
        # 797 - 203 / 782 - 218 / 795 - 205 / 820 - 180
        # 658 - 342 / 692 - 308 /
        sc2.run_game(sc2.maps.get(RANDOM_MAP), [BOT, Computer(Race.Protoss, Difficulty.CheatMoney)], realtime=False)
