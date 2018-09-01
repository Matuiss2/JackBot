import sc2, sys
from __init__ import run_ladder_game
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer

# Load bot
from ling_flood import EarlyAggro
bot = Bot(Race.Zerg, EarlyAggro())

# Start game
if __name__ == '__main__':
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        run_ladder_game(bot)
    else:
        # Local game
        print("Starting local game...")
        sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
            bot,
            #Bot(Race.Zerg, EarlyAggro())
            Computer(Race.Terran, Difficulty.CheatVision)
        ], realtime=False, save_replay_as="Example.SC2Replay")