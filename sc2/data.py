import enum
from typing import Dict, Set  # mypy type checking

from s2clientprotocol import common_pb2 as common_pb
from s2clientprotocol import data_pb2 as data_pb
from s2clientprotocol import error_pb2 as error_pb
from s2clientprotocol import raw_pb2 as raw_pb
from s2clientprotocol import sc2api_pb2 as sc_pb

from .ids.ability_id import AbilityId
from .ids.unit_typeid import UnitTypeId

# For the list of enums, see here

# https://github.com/Blizzard/s2client-api/blob/d9ba0a33d6ce9d233c2a4ee988360c188fbe9dbf/include/sc2api/sc2_gametypes.h
# https://github.com/Blizzard/s2client-api/blob/d9ba0a33d6ce9d233c2a4ee988360c188fbe9dbf/include/sc2api/sc2_action.h
# https://github.com/Blizzard/s2client-api/blob/d9ba0a33d6ce9d233c2a4ee988360c188fbe9dbf/include/sc2api/sc2_unit.h
# https://github.com/Blizzard/s2client-api/blob/d9ba0a33d6ce9d233c2a4ee988360c188fbe9dbf/include/sc2api/sc2_data.h


CREATE_GAME_ERROR = enum.Enum("CreateGameError", sc_pb.ResponseCreateGame.Error.items())

PLAYER_TYPE = enum.Enum("PlayerType", sc_pb.PlayerType.items())
DIFFICULTY = enum.Enum("Difficulty", sc_pb.Difficulty.items())
AI_BUILD = enum.Enum("AIBuild", sc_pb.AIBuild.items())
STATUS = enum.Enum("Status", sc_pb.Status.items())
RESULT = enum.Enum("Result", sc_pb.Result.items())
ALERT = enum.Enum("Alert", sc_pb.Alert.items())
CHAT_CHANNEL = enum.Enum("ChatChannel", sc_pb.ActionChat.Channel.items())

RACE = enum.Enum("Race", common_pb.Race.items())

DISPLAY_TYPE = enum.Enum("DisplayType", raw_pb.DisplayType.items())
ALLIANCE = enum.Enum("Alliance", raw_pb.Alliance.items())
CLOAK_STATE = enum.Enum("CloakState", raw_pb.CloakState.items())

ATTRIBUTE = enum.Enum("Attribute", data_pb.Attribute.items())
TARGET_TYPE = enum.Enum("TargetType", data_pb.Weapon.TargetType.items())
TARGET = enum.Enum("Target", data_pb.AbilityData.Target.items())

ACTION_RESULT = enum.Enum("ActionResult", error_pb.ActionResult.items())

race_worker: Dict[RACE, UnitTypeId] = {
    RACE.Protoss: UnitTypeId.PROBE,
    RACE.Terran: UnitTypeId.SCV,
    RACE.Zerg: UnitTypeId.DRONE,
}

race_townhalls: Dict[RACE, Set[UnitTypeId]] = {
    RACE.Protoss: {UnitTypeId.NEXUS},
    RACE.Terran: {
        UnitTypeId.COMMANDCENTER,
        UnitTypeId.ORBITALCOMMAND,
        UnitTypeId.PLANETARYFORTRESS,
        UnitTypeId.COMMANDCENTERFLYING,
        UnitTypeId.ORBITALCOMMANDFLYING,
    },
    RACE.Zerg: {UnitTypeId.HATCHERY, UnitTypeId.LAIR, UnitTypeId.HIVE},
}

warpgate_abilities: Dict[AbilityId, AbilityId] = {
    AbilityId.GATEWAYTRAIN_ZEALOT: AbilityId.WARPGATETRAIN_ZEALOT,
    AbilityId.GATEWAYTRAIN_STALKER: AbilityId.WARPGATETRAIN_STALKER,
    AbilityId.GATEWAYTRAIN_HIGHTEMPLAR: AbilityId.WARPGATETRAIN_HIGHTEMPLAR,
    AbilityId.GATEWAYTRAIN_DARKTEMPLAR: AbilityId.WARPGATETRAIN_DARKTEMPLAR,
    AbilityId.GATEWAYTRAIN_SENTRY: AbilityId.WARPGATETRAIN_SENTRY,
    AbilityId.TRAIN_ADEPT: AbilityId.TRAINWARP_ADEPT,
}

race_gas: Dict[RACE, UnitTypeId] = {
    RACE.Protoss: UnitTypeId.ASSIMILATOR,
    RACE.Terran: UnitTypeId.REFINERY,
    RACE.Zerg: UnitTypeId.EXTRACTOR,
}
