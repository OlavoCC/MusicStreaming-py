import asyncio
import yt_dlp

# ✅ CACHE GLOBAL (instantâneo nas próximas buscas)
audio_cache = {}

ytdl_opts = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",  # ← Mais rápido
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "cookiefile": "cookies.txt",
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
            "skip": ["hls", "dash"]
        }
    },
    # ✅ Remove postprocessors (não precisa pra streaming)
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)

async def search_music(termo):
    if not termo:
        return None

    # ✅ CACHE HIT = 0.01s (vs 3s)
    if termo in audio_cache:
        print(f"⚡ CACHE: {termo}")
        return audio_cache[termo]

    print(f"🔍 Buscando: {termo}")
    
    loop = asyncio.get_running_loop()
    info = await loop.run_in_executor(
        None,
        lambda: ytdl.extract_info(termo, download=False)
    )

    if "entries" in info:
        info = info["entries"][0]

    track = {
        "title": info.get("title"),
        "artist": info.get("uploader") or info.get("channel"),
        "url": info.get("webpage_url") or info.get("url"),  # ← url direto tb
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
    }

    # ✅ SALVA NO CACHE
    audio_cache[termo] = track
    print(f"✅ Cache salvo: {termo}")
    
    return track
