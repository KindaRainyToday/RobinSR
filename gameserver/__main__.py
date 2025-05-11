import asyncio
from gameserver.net.gateway import Gateway
from common.server_config import HOST, GAMESERVER_PORT
from common.util import Logger

if __name__ == "__main__":
    try:
        asyncio.run(Gateway.new(HOST, GAMESERVER_PORT))
    except Exception as e:
        Logger.error(e)
