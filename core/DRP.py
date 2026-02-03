import asyncio
from pypresence import Presence
import time
import dotenv
import os
dotenv.load_dotenv()
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")

class DiscordRPC:
    def __init__(self):
        self.rpc = Presence(CLIENT_ID)
        self.connected = False

    async def connect(self):
        """Agora é async - chame com await"""
        try:
            await asyncio.get_event_loop().run_in_executor(None, self.rpc.connect)
            self.connected = True
            print("✅ Discord RPC conectado!")
        except Exception as e:
            print("❌ Discord RPC não conectado:", e)

    async def update_playing(self, track):
        if not self.connected:
            return
        
        await asyncio.get_event_loop().run_in_executor(None, lambda: self.rpc.update(
            details=track["title"],
            state=f"por {track['artist']}",
            large_image=track["thumbnail"],
            large_text=track["title"],
            small_image="play",
            small_text="Tocando agora",
            start=int(time.time()),
            end=int(time.time()) + track["duration"],
            buttons=[{"label": "Ouvir no YouTube", "url": track["url"]}]
        ))

    async def update_paused(self, track):
        if not self.connected:
            return
        
        await asyncio.get_event_loop().run_in_executor(None, lambda: self.rpc.update(
            details=track["title"],
            state="Pausado",
            large_image=track["thumbnail"],
            small_image="pause",
            small_text="Pausado"
        ))

    async def clear(self):
        if self.connected:
            await asyncio.get_event_loop().run_in_executor(None, self.rpc.clear)
