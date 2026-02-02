import asyncio
import yt_dlp

ytdl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "cookiefile": "cookies.txt",  # ← Coloque o cookies.txt na pasta raiz do bot
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
            "skip": ["hls", "dash"]
        }
    },
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "opus",
    }],
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)

async def search_music(termo):
    if not termo:
        return None

    loop = asyncio.get_running_loop()

    info = await loop.run_in_executor(
        None,
        lambda: ytdl.extract_info(termo, download=False)
    )

    if "entries" in info:
        info = info["entries"][0]

    return {
        "title": info.get("title"),
        "url": info.get("url"),
        "duration": info.get("duration"),
    }






    