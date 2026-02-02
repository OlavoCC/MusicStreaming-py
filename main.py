import asyncio
import sys
from qasync import QEventLoop

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

import os

from core.search import search_music
from core.play import play_audio


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.current_track = None
        self.player_process = None

        loader = QUiLoader()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, "ui", "main.ui")

        ui_file = QFile(ui_path)
        ui_file.open(QFile.ReadOnly)

        self.ui = loader.load(ui_file, self)
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

        
    #############
    ##FUNCTIONS##
    #############
    async def on_play_clicked(self):
        if not self.current_track:
            QMessageBox.warning(
                self.ui,
                "Warning",
                "Nenhuma música carregada"
            )
            return
        if self.player_process:
            self.player_process.terminate()
        self.player_process = play_audio(self.current_track["url"])

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
        
        self.current_track = await search_music(termo)
        await QMessageBox.information(
            self.ui,
            "Search Result",
            f"Music Result: {termo}"
        )

    async def on_skip_clicked(self):
        pass

app = QApplication(sys.argv)

loop = QEventLoop(app)
asyncio.set_event_loop(loop)

window = MainWindow()
window.ui.show()

with loop:
    loop.run_forever()
