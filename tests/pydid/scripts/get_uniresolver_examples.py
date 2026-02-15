"""Retrieve uniresolver examples."""

import asyncio
import json
from pathlib import Path

import aiohttp

CONFIG_PATH = Path(__file__).parent / "uniresolver_config.json"
CONFIG = json.loads(CONFIG_PATH.read_text())
DIDS = [did for driver in CONFIG["drivers"] for did in driver["testIdentifiers"]]


async def fetch_doc(session, did: str):
    async with session.get(f"https://dev.uniresolver.io/1.0/identifiers/{did}") as resp:
        if resp.status == 200:
            return (await resp.json())["didDocument"]

        return None


async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for did in DIDS:
            tasks.append(asyncio.wait_for(fetch_doc(session, did), 20))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    results = [
        result
        for result in results
        if result is not None and not isinstance(result, asyncio.TimeoutError)
    ]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
