import subprocess

from core.search import search_music

ffmpeg_opts = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

def play_audio(audio_url):
    return subprocess.Popen([
        "ffmpeg",
        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-i", audio_url,
        "-vn",
        "-f", "pulse",  # funciona na maioria dos Linux
        "default"
    ])
    