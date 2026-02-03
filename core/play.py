import subprocess

from core.search import search_music

ffmpeg_opts = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

def play_audio(audio_url):
    ytdlp = subprocess.Popen([
        'yt-dlp', '-f', 'bestaudio[ext=m4a]', '--no-playlist', '-o', '-', audio_url
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    ffmpeg = subprocess.Popen([
        'ffmpeg', '-i', 'pipe:0', '-f', 'pulse', 'default'
    ], stdin=ytdlp.stdout)
    
    ytdlp.stdout.close()
    return ffmpeg
    