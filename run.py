"""Run the ladder or local game"""
import random
import sys
from sc2 import Race, Difficulty, AIBuild, run_game, maps
from sc2.player import Bot, Computer
from __init__ import run_ladder_game
from main import JackBot

if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        run_ladder_game(Bot(Race.Zerg, JackBot()))
    else:
        # Local game
        print("Starting local game...")
        MAP = random.choice(["BlueshiftLE", "KairosJunctionLE", "ParaSiteLE", "PortAleksanderLE"])
        BUILD = random.choice([AIBuild.Rush, AIBuild.Timing, AIBuild.Power, AIBuild.Macro, AIBuild.Air])
        DIFFICULTY = random.choice([Difficulty.CheatVision, Difficulty.CheatMoney, Difficulty.CheatInsane])
        RACE = random.choice([Race.Zerg, Race.Terran, Race.Protoss])
        print(f"\n{DIFFICULTY.name} {RACE.name} {BUILD.name} {MAP}")
        BOT = Bot(Race.Zerg, JackBot())
        BUILTIN_BOT = Computer(RACE, DIFFICULTY, BUILD)
        run_game(maps.get(MAP), [BOT, BUILTIN_BOT], realtime=False)
