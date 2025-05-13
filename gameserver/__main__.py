import asyncio
from gameserver.net.gateway import Gateway
from common.server_config import HOST, GAMESERVER_PORT
from common.util import Logger
from common.resources import GAME_RES

if __name__ == "__main__":
    try:
        Logger.info("Loading GAME_RES")
        _ = GAME_RES
        Logger.info("Starting server.")
        asyncio.run(Gateway.new(HOST, GAMESERVER_PORT))
    except Exception as e:
        Logger.error(e)
