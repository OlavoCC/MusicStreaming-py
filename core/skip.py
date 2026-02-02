import asyncio

async def skip_music():
    await asyncio.sleep(1)
    return "Skipped"