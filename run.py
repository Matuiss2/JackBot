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
        while True:
            # for security purposes, pointless in this scenario but do it anyway to get used to it
            SECURE_RANDOM = random.SystemRandom()
            MAP = SECURE_RANDOM.choice(["BlueshiftLE", "KairosJunctionLE", "ParaSiteLE", "PortAleksanderLE"])
            BUILD = SECURE_RANDOM.choice([AIBuild.Macro, AIBuild.Rush, AIBuild.Timing, AIBuild.Power, AIBuild.Air])
            DIFFICULTY = SECURE_RANDOM.choice([Difficulty.CheatInsane, Difficulty.CheatVision, Difficulty.CheatMoney])
            RACE = SECURE_RANDOM.choice([Race.Protoss, Race.Zerg, Race.Terran])
            FINISHED_SETS = {
                BUILD == AIBuild.Macro and DIFFICULTY == Difficulty.CheatInsane and RACE == Race.Terran,
                BUILD == AIBuild.Power and DIFFICULTY == Difficulty.CheatInsane and RACE == Race.Zerg,
                BUILD == AIBuild.Rush and DIFFICULTY == Difficulty.CheatInsane and RACE == Race.Zerg,
                BUILD == AIBuild.Timing and DIFFICULTY == Difficulty.CheatMoney and RACE == Race.Protoss,

            }
            if any(FINISHED_SETS):
                print(f"{DIFFICULTY.name} {RACE.name} {BUILD.name} already done")
                continue
            break
        print(f"{DIFFICULTY.name} {RACE.name} {BUILD.name}")
        BOT = Bot(Race.Zerg, JackBot())
        BUILTIN_BOT = Computer(RACE, DIFFICULTY, BUILD)
        run_game(maps.get(MAP), [BOT, BUILTIN_BOT], realtime=False)
