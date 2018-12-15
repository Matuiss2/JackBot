"""Group everything that defines a player"""
from .bot_ai import BotAI
from .data import DIFFICULTY, PLAYER_TYPE, RACE


class AbstractPlayer:
    """Define what the all player types have in common"""

    def __init__(self, tipo, race=None, difficulty=None):
        assert isinstance(tipo, PLAYER_TYPE)
        if tipo == PLAYER_TYPE.Computer:
            assert isinstance(difficulty, DIFFICULTY)
        elif tipo == PLAYER_TYPE.Observer:
            assert race is None
            assert difficulty is None
        else:
            assert isinstance(race, RACE)
            assert difficulty is None
        self.type = tipo
        if race:
            self.race = race
        if tipo == PLAYER_TYPE.Computer:
            self.difficulty = difficulty


class Human(AbstractPlayer):
    """Set the player type(human) and its race"""

    def __init__(self, race):
        super().__init__(PLAYER_TYPE.Participant, race)

    def __str__(self):
        return f"Human({self.race})"


class Bot(AbstractPlayer):
    """Set the player type(bot) and its race"""

    def __init__(self, race, ai):
        assert isinstance(ai, BotAI) or ai is None
        super().__init__(PLAYER_TYPE.Participant, race)
        self.ai = ai

    def __str__(self):
        return f"Bot({self.race}, {self.ai})"


class Computer(AbstractPlayer):
    """Set the player type(built-in ai), its race and difficulty"""

    def __init__(self, race, difficulty=DIFFICULTY.Easy):
        super().__init__(PLAYER_TYPE.Computer, race, difficulty)

    def __str__(self):
        return f"Computer({self.race}, {self.difficulty})"


class Observer(AbstractPlayer):
    """Creates the observer"""

    def __init__(self):
        super().__init__(PLAYER_TYPE.Observer)

    def __str__(self):
        return f"Observer()"


class Player(AbstractPlayer):
    """creates player of all 3 types"""

    @classmethod
    def from_proto(cls, proto):
        """Take necessary info from the protocol and creates player of all 3 types"""
        if PLAYER_TYPE(proto.type) == PLAYER_TYPE.Observer:
            return cls(proto.player_id, PLAYER_TYPE(proto.type), None, None, None)
        return cls(
            proto.player_id,
            PLAYER_TYPE(proto.type),
            RACE(proto.race_requested),
            DIFFICULTY(proto.difficulty) if proto.HasField("difficulty") else None,
            RACE(proto.race_actual) if proto.HasField("race_actual") else None,
        )

    def __init__(self, player_id, tipo, requested_race, difficulty=None, actual_race=None):
        super().__init__(tipo, requested_race, difficulty)
        self.id: int = player_id
        self.actual_race: RACE = actual_race
