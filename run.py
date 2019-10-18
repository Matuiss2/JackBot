"""Run the ladder or local game"""
import random
import sys
from sc2 import maps
from sc2.main import run_game
from sc2.player import Bot, Computer, RACE, AI_BUILD, DIFFICULTY
from __init__ import run_ladder_game
from main import JackBot

if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        run_ladder_game(Bot(RACE.Zerg, JackBot()))
    else:
        # Local game
        while True:
            # for security purposes, pointless in this scenario but do it anyway to get used to it
            SECURE_RANDOM = random.SystemRandom()
            MAP = SECURE_RANDOM.choice(["BlueshiftLE", "KairosJunctionLE", "ParaSiteLE", "PortAleksanderLE"])
            BUILD = SECURE_RANDOM.choice([AI_BUILD.Macro, AI_BUILD.Rush, AI_BUILD.Timing, AI_BUILD.Power, AI_BUILD.Air])
            DIFFICULTY = SECURE_RANDOM.choice([DIFFICULTY.CheatInsane, DIFFICULTY.CheatVision, DIFFICULTY.CheatMoney])
            RACE = SECURE_RANDOM.choice([RACE.Protoss, RACE.Zerg, RACE.Terran])
            """FINISHED_SETS = {
                BUILD == AIBuild.Macro and DIFFICULTY == Difficulty.CheatVision and RACE == Race.Zerg,
            }
            if any(FINISHED_SETS):
                print(f"{DIFFICULTY.name} {RACE.name} {BUILD.name} already done")
                continue"""
            break
        print(f"{DIFFICULTY.name} {RACE.name} {BUILD.name}")
        BOT = Bot(RACE.Zerg, JackBot())
        BUILTIN_BOT = Computer(RACE, DIFFICULTY, BUILD)
        run_game(maps.get(MAP), [BOT, BUILTIN_BOT], realtime=False)
