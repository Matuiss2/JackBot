"""Group constants"""
import enum
from typing import Dict, Set
from s2clientprotocol import common_pb2 as common_pb
from s2clientprotocol import data_pb2 as data_pb
from s2clientprotocol import error_pb2 as error_pb
from s2clientprotocol import raw_pb2 as raw_pb
from s2clientprotocol import sc2api_pb2 as sc_pb
from .ids.ability_id import AbilityId
from .ids.unit_typeid import UnitTypeId


CREATE_GAME_ERROR = enum.Enum("CREATE_GAME_ERROR", sc_pb.ResponseCreateGame.Error.items())
PLAYER_TYPE = enum.Enum("PLAYER_TYPE", sc_pb.PlayerType.items())
DIFFICULTY = enum.Enum("Difficulty", sc_pb.Difficulty.items())
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
    RACE.Terran: {UnitTypeId.COMMANDCENTER, UnitTypeId.ORBITALCOMMAND, UnitTypeId.PLANETARYFORTRESS},
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
