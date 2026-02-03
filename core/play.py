import subprocess
import signal
import os

def play_audio(audio_url):
    ytdlp_cmd = [
        'yt-dlp', 
        '-f', 'bestaudio[ext=m4a]/bestaudio[ext=mp4]/bestaudio',
        '--no-playlist', '-o', '-', '--quiet', '--no-warnings',
        audio_url
    ]
    
    ffmpeg_cmd = [
        'ffmpeg', '-loglevel', 'error', '-threads', '2',
        '-i', 'pipe:0', '-f', 'pulse', 'default',
        '-ar', '44100', '-ac', '2'
    ]
    
    # ✅ SEM start_new_session=True (causador do problema)
    ytdlp = subprocess.Popen(
        ytdlp_cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.DEVNULL,
        bufsize=16384
    )
    
    ffmpeg = subprocess.Popen(
        ffmpeg_cmd,
        stdin=ytdlp.stdout,
        stderr=subprocess.DEVNULL
    )
    
    ytdlp.stdout.close()
    
    # ✅ RETORNA OS DOIS PROCESSOS (pra matar tudo)
    return (ffmpeg, ytdlp)
