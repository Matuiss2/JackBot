from .bot_ai import BotAI
from .data import AI_BUILD, DIFFICULTY, PLAYER_TYPE, RACE


class AbstractPlayer:
    def __init__(self, p_type, race=None, name=None, difficulty=None, ai_build=None, fullscreen=False):
        assert isinstance(p_type, PLAYER_TYPE), f"p_type is of type {type(p_type)}"
        assert name is None or isinstance(name, str), f"name is of type {type(name)}"

        self.name = name
        self.type = p_type
        self.fullscreen = fullscreen
        if race is not None:
            self.race = race
        if p_type == PLAYER_TYPE.Computer:
            assert isinstance(difficulty, DIFFICULTY), f"difficulty is of type {type(difficulty)}"
            # Workaround, proto information does not carry ai_build info
            # We cant set that in the Player classmethod
            assert ai_build is None or isinstance(ai_build, AI_BUILD), f"ai_build is of type {type(ai_build)}"
            self.difficulty = difficulty
            self.ai_build = ai_build

        elif p_type == PLAYER_TYPE.Observer:
            assert race is None
            assert difficulty is None
            assert ai_build is None

        else:
            assert isinstance(race, RACE), f"race is of type {type(race)}"
            assert difficulty is None
            assert ai_build is None


class Human(AbstractPlayer):
    def __init__(self, race, name=None, fullscreen=False):
        super().__init__(PLAYER_TYPE.Participant, race, name=name, fullscreen=fullscreen)

    def __str__(self):
        if self.name is not None:
            return f"Human({self.race._name_}, name={self.name !r})"
        return f"Human({self.race._name_})"


class Bot(AbstractPlayer):
    def __init__(self, race, ai, name=None, fullscreen=False):
        """
        AI can be None if this player object is just used to inform the
        server about player types.
        """
        assert isinstance(ai, BotAI) or ai is None, f"ai is of type {type(ai)}, inherit BotAI from bot_ai.py"
        super().__init__(PLAYER_TYPE.Participant, race, name=name, fullscreen=fullscreen)
        self.ai = ai

    def __str__(self):
        if self.name is not None:
            return f"Bot {self.ai.__class__.__name__}({self.race._name_}), name={self.name !r})"
        return f"Bot {self.ai.__class__.__name__}({self.race._name_})"


class Computer(AbstractPlayer):
    def __init__(self, race, difficulty=DIFFICULTY.Easy, ai_build=AI_BUILD.RandomBuild):
        super().__init__(PLAYER_TYPE.Computer, race, difficulty=difficulty, ai_build=ai_build)

    def __str__(self):
        return f"Computer {self.difficulty._name_}({self.race._name_}, {self.ai_build.name})"


class Observer(AbstractPlayer):
    def __init__(self):
        super().__init__(PLAYER_TYPE.Observer)

    def __str__(self):
        return f"Observer"


class Player(AbstractPlayer):
    @classmethod
    def from_proto(cls, proto):
        if PLAYER_TYPE(proto.type) == PLAYER_TYPE.Observer:
            return cls(proto.player_id, PLAYER_TYPE(proto.type), None, None, None)
        return cls(
            proto.player_id,
            PLAYER_TYPE(proto.type),
            RACE(proto.race_requested),
            DIFFICULTY(proto.difficulty) if proto.HasField("difficulty") else None,
            RACE(proto.race_actual) if proto.HasField("race_actual") else None,
            proto.player_name if proto.HasField("player_name") else None,
        )

    def __init__(self, player_id, p_type, requested_race, difficulty=None, actual_race=None, name=None, ai_build=None):
        super().__init__(p_type, requested_race, difficulty=difficulty, name=name, ai_build=ai_build)
        self.id: int = player_id
        self.actual_race: RACE = actual_race
