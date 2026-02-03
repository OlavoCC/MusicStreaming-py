import asyncio
import sys
import qasync
from qasync import QEventLoop

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QStringListModel, QFile
from core.DRP import DiscordRPC
import os

from core.search import search_music
from core.play import play_audio

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.player_processes = None
        self.current_track_index = -1
        self.queue = []
        self.is_playing = False
        self.wait_task = None

        loader = QUiLoader()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, "ui", "main.ui")

        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.playlist_model = QStringListModel()
        self.ui.LVplaylist.setModel(self.playlist_model)
        self.rpc = DiscordRPC()
        ui_file.close()

        # ✅ CONEXÕES DIRETAS com @asyncSlot
        self.ui.BtnContinue.clicked.connect(self.on_play_clicked)
        self.ui.BtnPause.clicked.connect(self.on_pause_clicked)
        self.ui.BtnReturn.clicked.connect(self.on_return_clicked)
        self.ui.BtnBusca.clicked.connect(self.on_search_clicked)
        self.ui.BtnRepeat.clicked.connect(self.on_repeat_clicked)
        self.ui.BtnSkip.clicked.connect(self.on_skip_clicked)
        self.ui.LVplaylist.clicked.connect(self.on_playlist_clicked)

    #############
    ##FUNCTIONS##
    #############
    
    @qasync.asyncSlot()
    async def on_play_clicked(self):
        if not self.queue:
            QMessageBox.warning(self.ui, "Warning", "Playlist vazia")
            return
        if not self.is_playing:
            await self.play_next()

    # on_pause_clicked, on_skip_clicked:
    @qasync.asyncSlot()
    async def on_pause_clicked(self):
        if self.player_processes:  # ← player_processes
            ffmpeg, ytdlp = self.player_processes
            ffmpeg.terminate()
            ytdlp.terminate()
            self.player_processes = None
    
        if self.queue:
            await self.rpc.update_paused(self.queue[0])

    @qasync.asyncSlot()
    async def on_return_clicked(self):
        pass

    @qasync.asyncSlot()
    async def on_repeat_clicked(self):
        pass
    
    @qasync.asyncSlot()
    async def on_search_clicked(self):
        termo = self.ui.Txtbox.text().strip()
        if not termo:
            QMessageBox.warning(self.ui, "Warning", "Campo vazio")
            return
        await self.add_to_playlist(termo)
        QMessageBox.information(self.ui, "Search Result", f"Music Result: {termo}")

    @qasync.asyncSlot()
    async def on_skip_clicked(self):
        if not self.queue:
            return
    
    # ✅ CANCELA task E MATA PROCESSOS
        if self.wait_task and not self.wait_task.done():
            self.wait_task.cancel()
            self.wait_task = None
    
        if self.player_processes:  # ← player_processes (NOVO)
            ffmpeg, ytdlp = self.player_processes
            ffmpeg.terminate()
            ytdlp.terminate()
            self.player_processes = None
    
        self.queue.pop(0)
        self.update_playlist_view()
        await self.play_next()
    
    @qasync.asyncSlot()
    async def on_playlist_clicked(self, index):
        pass
    
    ####################
    ##FUNC TO PLAYLIST##
    #####################
    
    async def add_to_playlist(self, termo):
        track = await search_music(termo)
        if not track:
            return
        self.queue.append(track)
        self.update_playlist_view()  # ✅ AGORA EXISTE!
        if not self.is_playing:
            await self.play_next()

    # play_next:
    async def play_next(self):
        if not self.queue:
            self.is_playing = False
            await self.rpc.clear()
            return

        self.is_playing = True
    
    # Cancela task anterior
        if self.wait_task and not self.wait_task.done():
            self.wait_task.cancel()
    
        track = self.queue[0]
        self.player_processes = play_audio(track["url"])  # ← Retorna (ffmpeg, ytdlp)
        self.current_track_index = 0
    
        self.wait_task = asyncio.create_task(self.wait_song_end())
        await self.rpc.update_playing(track)


    async def wait_song_end(self):
        if not self.player_processes:
            return
        
        loop = asyncio.get_running_loop()
        ffmpeg, ytdlp = self.player_processes
    
        await loop.run_in_executor(None, ffmpeg.wait)
    
        if self.current_track_index != 0:
            return

        if self.queue:
            self.queue.pop(0)
            self.update_playlist_view()
        
        self.player_processes = None
        self.current_track_index = -1
        await self.play_next()

    # ✅ FUNÇÃO QUE FALTAVA!
    def update_playlist_view(self):
        titles = [track["title"] for track in self.queue]
        self.playlist_model.setStringList(titles)

# ✅ CORREÇÃO DO EVENT LOOP
app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)

window = MainWindow()
window.ui.show()

# Conecta RPC NO EVENT LOOP CORRETO
loop.call_soon_threadsafe(lambda: asyncio.create_task(window.rpc.connect()))

with loop:
    loop.run_forever()
