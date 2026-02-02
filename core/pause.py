import asyncio

async def pause_music():
    await asyncio.sleep(1)
    return "Paused"