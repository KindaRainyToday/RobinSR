import asyncio
from gameserver.net.gateway import Gateway
from gameserver.net.packet import RSP_MAP
from gameserver.net.handlers.dummy import DUMMY_MAP
from common.server_config import HOST, GAMESERVER_PORT
from common.util import Logger
from common.resources import GAME_RES

if __name__ == "__main__":
    try:
        Logger.info("Loading GAME_RES & Handlers")
        # print(id(...))-ing these will show that their memory address didn't change :)
        # they're only loaded once and kept in memory
        _1 = GAME_RES
        _2 = RSP_MAP
        _3 = DUMMY_MAP
        Logger.info("Starting server.")
        asyncio.run(Gateway.new(HOST, GAMESERVER_PORT))
    except Exception as e:
        Logger.error(e)
