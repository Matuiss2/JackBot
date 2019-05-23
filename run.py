"""Run the ladder or local game"""
import itertools
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
        MAPS = ["BlueshiftLE", "KairosJunctionLE", "ParaSiteLE", "PortAleksanderLE"]
        BUILDS = [AIBuild.Rush, AIBuild.Timing, AIBuild.Power, AIBuild.Macro, AIBuild.Air]
        DIFFICULTIES = [
            Difficulty.VeryEasy,
            Difficulty.Easy,
            Difficulty.Medium,
            Difficulty.MediumHard,
            Difficulty.Hard,
            Difficulty.Harder,
            Difficulty.VeryHard,
            Difficulty.CheatVision,
            Difficulty.CheatMoney,
            Difficulty.CheatInsane,
        ]
        RACES = [Race.Zerg, Race.Terran, Race.Protoss]
        for selected_map, build, dif, race in itertools.product(MAPS, BUILDS, DIFFICULTIES, RACES):
            print("\n" + str(dif.name), str(race.name))
            bot = Bot(Race.Zerg, JackBot())
            builtin_bot = Computer(race, dif, build)
            run_game(maps.get(selected_map), [bot, builtin_bot], realtime=False)
