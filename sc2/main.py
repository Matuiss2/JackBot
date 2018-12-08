"""Group everything needed to start a game"""
import logging
import asyncio
import async_timeout
from .sc2process import SC2Process
from .portconfig import Portconfig
from .client import Client
from .player import Human, Bot
from .data import RESULT, CREATE_GAME_ERROR
from .game_state import GameState
from .protocol import ConnectionAlreadyClosed

LOGGER = logging.getLogger(__name__)


async def play_game_human(client, player_id, realtime, game_time_limit):
    """Allow humans to play"""
    while True:
        state = await client.observation()
        if client.game_result:
            return client.game_result[player_id]
        if game_time_limit and (state.observation.observation.game_loop * 0.725 * (1 / 16)) > game_time_limit:
            print(state.observation.game_loop, state.observation.game_loop * 0.14)
            return RESULT.Tie
        if not realtime:
            await client.step()


async def play_game_ai(client, player_id, ai, realtime, step_time_limit, game_time_limit):
    """Allow bots to play"""
    game_data = await client.get_game_data()
    game_info = await client.get_game_info()
    ai.prepare_start(client, player_id, game_info, game_data)
    ai.on_start()
    iteration = 0
    while True:
        state = await client.observation()
        if client.game_result:
            ai.on_end(client.game_result[player_id])
            return client.game_result[player_id]
        game_state = GameState(state.observation, game_data)
        if game_time_limit and (game_state.game_loop * 0.725 * (1 / 16)) > game_time_limit:
            ai.on_end(RESULT.Tie)
            return RESULT.Tie
        ai.prepare_step(game_state)
        if not iteration:
            ai.prepare_first_step()
        LOGGER.debug(f"Running AI step, realtime={realtime}")
        try:
            await ai.issue_events()
            if realtime:
                await ai.on_step(iteration)
            else:
                LOGGER.debug(f"Running AI step, timeout={step_time_limit}")
                try:
                    async with async_timeout.timeout(step_time_limit):
                        await ai.on_step(iteration)
                except asyncio.TimeoutError:
                    LOGGER.warning("Running AI step: out of time")
        except Exception:
            LOGGER.exception("AI step threw an error")
            LOGGER.error("resigning due to previous error")
            ai.on_end(RESULT.Defeat)
            return RESULT.Defeat
        LOGGER.debug("Running AI step: done")
        if not realtime:
            if not client.in_game:  # Client left (resigned) the game
                ai.on_end(client.game_result[player_id])
                return client.game_result[player_id]
            await client.step()
        iteration += 1


async def play_game(player, client, realtime, portconfig, step_time_limit=None, game_time_limit=None):
    """Put the players on the game and prints the result of it"""
    assert isinstance(realtime, bool), repr(realtime)
    player_id = await client.join_game(player.race, portconfig=portconfig)
    if isinstance(player, Human):
        result = await play_game_human(client, player_id, realtime, game_time_limit)
    else:
        result = await play_game_ai(client, player_id, player.ai, realtime, step_time_limit, game_time_limit)
    logging.info(f"Result for player id: {player_id}: {result}")
    return result


async def _setup_host_game(server, map_settings, players, realtime):
    """Connect to battlenet and create this game"""
    connect_to_server = await server.create_game(map_settings, players, realtime)
    if connect_to_server.create_game.HasField("error"):
        err = f"Could not create game: {CREATE_GAME_ERROR(connect_to_server.create_game.error)}"
        if connect_to_server.create_game.HasField("error_details"):
            err += f": {connect_to_server.create_game.error_details}"
        LOGGER.critical(err)
        raise RuntimeError(err)
    return Client(server.ws)


async def _host_game(
    map_settings, players, realtime, portconfig=None, save_replay_as=None, step_time_limit=None, game_time_limit=None
):
    """Group requirements to host the game and create a replay for it"""
    assert players, "Can't create a game without players"
    assert any(isinstance(p, (Human, Bot)) for p in players)
    async with SC2Process() as server:
        await server.ping()
        client = await _setup_host_game(server, map_settings, players, realtime)
        try:
            result = await play_game(players[0], client, realtime, portconfig, step_time_limit, game_time_limit)
            if save_replay_as:
                await client.save_replay(save_replay_as)
            await client.leave()
            await client.quit()
        except ConnectionAlreadyClosed:
            logging.error(f"Connection was closed before the game ended")
            return None
        return result


async def _host_game_aiter(
    map_settings, players, realtime, portconfig=None, save_replay_as=None, step_time_limit=None, game_time_limit=None
):
    """Group requirements to host some games and create a replay for it"""
    assert players, "Can't create a game without players"
    assert any(isinstance(p, (Human, Bot)) for p in players)
    async with SC2Process() as server:
        while True:
            await server.ping()
            client = await _setup_host_game(server, map_settings, players, realtime)
            try:
                result = await play_game(players[0], client, realtime, portconfig, step_time_limit, game_time_limit)
                if save_replay_as:
                    await client.save_replay(save_replay_as)
                await client.leave()
            except ConnectionAlreadyClosed:
                logging.error(f"Connection was closed before the game ended")
                return
            new_players = yield result
            if new_players:
                players = new_players


def _host_game_iter(*args, **kwargs):
    """Not sure what it does"""
    game = _host_game_aiter(*args, **kwargs)
    new_playerconfig = None
    while True:
        new_playerconfig = yield asyncio.get_event_loop().run_until_complete(game.asend(new_playerconfig))


async def _join_game(players, realtime, portconfig, save_replay_as=None, step_time_limit=None, game_time_limit=None):
    """Group requirements to host the game and create a replay for it"""
    async with SC2Process() as server:
        await server.ping()
        client = Client(server.ws)
        try:
            result = await play_game(players[1], client, realtime, portconfig, step_time_limit, game_time_limit)
            if save_replay_as:
                await client.save_replay(save_replay_as)
            await client.leave()
            await client.quit()
        except ConnectionAlreadyClosed:
            logging.error(f"Connection was closed before the game ended")
            return None
        return result


def run_game(map_settings, players, **kwargs):
    """Check the requirements for starting the game then run it"""
    if sum(isinstance(p, (Human, Bot)) for p in players) > 1:
        join_kwargs = {k: v for k, v in kwargs.items() if k != "save_replay_as"}
        portconfig = Portconfig()
        result = asyncio.get_event_loop().run_until_complete(
            asyncio.gather(
                _host_game(map_settings, players, **kwargs, portconfig=portconfig),
                _join_game(players, **join_kwargs, portconfig=portconfig),
            )
        )
    else:
        result = asyncio.get_event_loop().run_until_complete(_host_game(map_settings, players, **kwargs))
    return result
