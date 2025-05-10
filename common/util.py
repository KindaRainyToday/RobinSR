import aiofiles
from typing import Any
from pathlib import Path


class AsyncFs:
    @staticmethod
    async def read_to_str(path: str) -> str:
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            return await f.read()

    @staticmethod
    async def write_to_file(path: str, content: str) -> None:
        async with aiofiles.open(path, mode="w", encoding="utf-8") as f:
            await f.write(content)


class SyncFs:
    @staticmethod
    def read_to_str(path: str) -> str:
        return Path(path).read_text()

    @staticmethod
    def write_to_file(path: str, content: str) -> None:
        Path(path).write_text(content)


class Logger:
    @staticmethod
    def error(c: Any) -> None:
        print(f"ERROR: {c}")

    @staticmethod
    def info(c: Any) -> None:
        print(f"INFO: {c}")

    @staticmethod
    def warn(c: Any) -> None:
        print(f"WARN: {c}")

    @staticmethod
    def debug(c: Any) -> None:
        print(f"DEBUG: {c}")
