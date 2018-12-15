"""Groups some info about the all global(shared by all races) state of sc2 so it can be used in an easy way"""
from typing import List, Set
from .data import ALLIANCE, DISPLAY_TYPE
from .ids.effect_id import EffectId
from .ids.upgrade_id import UpgradeId
from .pixel_map import PixelMap
from .position import Point2, Point3
from .power_source import PsionicMatrix
from .score import ScoreDetails
from .units import Units


class Blip:
    """Identifies and categorize the visible units"""

    def __init__(self, proto):
        self.proto = proto

    @property
    def is_blip(self) -> bool:
        """Detected by sensor tower."""
        return self.proto.is_blip

    @property
    def is_snapshot(self) -> bool:
        """Detected for just a small moment(f.e tanks that shoot you on the high ground)"""
        return self.proto.display_type == DISPLAY_TYPE.Snapshot.value

    @property
    def is_visible(self) -> bool:
        """Detected- its outside the fog of war"""
        return self.proto.display_type == DISPLAY_TYPE.Visible.value

    @property
    def alliance(self) -> ALLIANCE:
        """Its an ally's unit"""
        return self.proto.alliance

    @property
    def is_mine(self) -> bool:
        """Its a bot's unit"""
        return self.proto.alliance == ALLIANCE.Self.value

    @property
    def is_enemy(self) -> bool:
        """Its an enemy unit"""
        return self.proto.alliance == ALLIANCE.Enemy.value

    @property
    def position(self) -> Point2:
        """2d position of the blip."""
        return self.position3d.to2

    @property
    def position3d(self) -> Point3:
        """3d position of the blip."""
        return Point3.from_proto(self.proto.pos)


class Common:
    """Groups every common attributes for every race"""

    ATTRIBUTES = [
        "player_id",
        "minerals",
        "vespene",
        "food_cap",
        "food_used",
        "food_army",
        "food_workers",
        "idle_worker_count",
        "army_count",
        "warp_gate_count",
        "larva_count",
    ]

    def __init__(self, proto):
        self.proto = proto

    def __getattr__(self, attr):
        assert attr in self.ATTRIBUTES, f"'{attr}' is not a valid attribute"
        return int(getattr(self.proto, attr))


class EffectData:
    """Group all effects and its position"""

    def __init__(self, proto):
        self.proto = proto

    @property
    def id(self) -> EffectId:
        """Get the id of the effect"""
        return EffectId(self.proto.effect_id)

    @property
    def positions(self) -> List[Point2]:
        """List all positions that are targets by the effect"""
        return [Point2.from_proto(p) for p in self.proto.pos]


class GameState:
    """Groups most useful info about the game state"""

    def __init__(self, response_observation, game_data):
        self.actions = response_observation.actions
        self.action_errors = response_observation.action_errors
        self.observation = response_observation.observation
        self.player_result = response_observation.player_result
        self.chat = response_observation.chat
        self.common: Common = Common(self.observation.player_common)
        self.psionic_matrix: PsionicMatrix = PsionicMatrix.from_proto(self.observation.raw_data.player.power_sources)
        self.game_loop: int = self.observation.game_loop
        self.score: ScoreDetails = ScoreDetails(self.observation.score)
        self.abilities = self.observation.abilities
        destructible = [x for x in self.observation.raw_data.units if x.alliance == 3 and x.radius > 1.5]
        self.destructible: Units = Units.from_proto(destructible, game_data)
        visible_units, hidden_units = [], []
        for unit in self.observation.raw_data.units:
            if unit.is_blip:
                hidden_units.append(unit)
            else:
                visible_units.append(unit)
        self.units: Units = Units.from_proto(visible_units, game_data)
        self.blips: Set[Blip] = {Blip(unit) for unit in hidden_units}
        self.visibility: PixelMap = PixelMap(self.observation.raw_data.map_state.visibility)
        self.creep: PixelMap = PixelMap(self.observation.raw_data.map_state.creep)
        self.dead_units: Set[int] = {dead_unit_tag for dead_unit_tag in self.observation.raw_data.event.dead_units}
        self.effects: Set[EffectData] = {EffectData(effect) for effect in self.observation.raw_data.effects}
        self.upgrades: Set[UpgradeId] = {UpgradeId(upgrade) for upgrade in self.observation.raw_data.player.upgrade_ids}

    @property
    def mineral_field(self) -> Units:
        """Return all mineral patches info"""
        return self.units.mineral_field

    @property
    def vespene_geyser(self) -> Units:
        """Return all geysers info"""
        return self.units.vespene_geyser
