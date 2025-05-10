import aiofiles


async def async_read_to_str(path: str) -> str:
    async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
        return await f.read()


async def async_write_to_file(path: str, content: str) -> None:
    async with aiofiles.open(path, mode="w", encoding="utf-8") as f:
        await f.write(content)
