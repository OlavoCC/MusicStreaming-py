import asyncio
import sys
from qasync import QEventLoop

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QStringListModel
from PySide6.QtCore import QFile

import os

from core.search import search_music
from core.play import play_audio


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.player_process = None
        self.queue = []
        self.is_playing = False
        self.player_process = None


        loader = QUiLoader()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, "ui", "main.ui")

        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)

        self.ui = loader.load(ui_file, self)
        self.playlist_model = QStringListModel()
        self.ui.LVplaylist.setModel(self.playlist_model)
        ui_file.close()

        self.ui.BtnContinue.clicked.connect(
            lambda: asyncio.create_task(self.on_play_clicked())
        )
        self.ui.BtnPause.clicked.connect(
            lambda: asyncio.create_task(self.on_pause_clicked())
        )
        self.ui.BtnReturn.clicked.connect(
            lambda: asyncio.create_task(self.on_return_clicked())
        )
        self.ui.BtnBusca.clicked.connect(
            lambda: asyncio.create_task(self.on_search_clicked())
        )
        self.ui.BtnRepeat.clicked.connect(
            lambda: asyncio.create_task(self.on_repeat_clicked())
        )
        self.ui.BtnSkip.clicked.connect(
            lambda: asyncio.create_task(self.on_skip_clicked())
        )
        self.ui.LVplaylist.clicked.connect(
            lambda index: asyncio.create_task(
                self.on_playlist_clicked(index)
            )
        )   


        
    #############
    ##FUNCTIONS##
    #############
    async def on_play_clicked(self):
        if not self.queue:
            QMessageBox.warning(
                self.ui,
                "Warning",
                "Playlist vazia"
            )
            return

        if not self.is_playing:
            await self.play_next()


    async def on_pause_clicked(self):
        if self.player_process:
            self.player_process.terminate()
            self.player_process = None

    async def on_return_clicked(self):
        pass

    async def on_repeat_clicked(self):
        pass
    
    async def on_search_clicked(self):
        termo = self.ui.Txtbox.text().strip()
        if not termo:
            QMessageBox.warning(
                self.ui,
                "Warning",
                "Campo vazio"
            )
            return
        
        await self.add_to_playlist(termo)
        QMessageBox.information(
            self.ui,
            "Search Result",
            f"Music Result: {termo}"
        )

    async def on_skip_clicked(self):
        if not self.queue:
            return

        if self.player_process:
            self.player_process.terminate()
            self.player_process = None

        self.queue.pop(0)
        self.update_playlist_view()
        await self.play_next()
    
    ####################
    ##FUNC TO PLAYLIST##
    #####################

    async def add_to_playlist(self, termo):
        track = await search_music(termo)

        if not track:
            return

        self.queue.append(track)
        self.update_playlist_view()
        if not self.is_playing:
            await self.play_next()

    async def play_next(self):
        if not self.queue:
            self.is_playing = False
            return

        self.is_playing = True
        track = self.queue[0]

        self.player_process = play_audio(track["url"])

        asyncio.create_task(self.wait_song_end())
    
    async def wait_song_end(self):
        loop = asyncio.get_running_loop()

        await loop.run_in_executor(
            None,
            self.player_process.wait
        )

    # Se foi parado manualmente (skip/pause)
        if not self.player_process:
            return

        if self.queue:
            self.queue.pop(0)
            self.update_playlist_view()

        await self.play_next()
    def update_playlist_view(self):
        titles = [track["title"] for track in self.queue]
        self.playlist_model.setStringList(titles)

    #######
    ##END##
    #######

app = QApplication(sys.argv)

loop = QEventLoop(app)
asyncio.set_event_loop(loop)

window = MainWindow()
window.ui.show()

with loop:
    loop.run_forever()
