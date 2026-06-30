# main.py
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, NavigationItemPosition, FluentIcon as FIF, setTheme, Theme

from i18n import tr
from views.packer_interface import PackerInterface
from views.settings_interface import SettingsInterface

class DevToolsMainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.init_window()
        self.init_navigation()

    def init_window(self):
        self.setWindowTitle("BetterLyrics DevTools")
        self.resize(800, 700)
        self.setMinimumSize(700, 600)
        
        self.packer_interface = PackerInterface(self)
        self.settings_interface = SettingsInterface(self)
        
        # 绑定语言切换信号以实时刷新 UI 文本
        self.settings_interface.langChanged.connect(self.on_language_changed)

    def init_navigation(self):
        self.addSubInterface(self.packer_interface, FIF.APPLICATION, tr("nav_packer"))
        self.addSubInterface(self.settings_interface, FIF.SETTING, tr("nav_settings"), NavigationItemPosition.BOTTOM)

    def on_language_changed(self):
        self.packer_interface.update_texts()
        self.settings_interface.update_texts()

if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)

    setTheme(Theme.DARK)
    
    window = DevToolsMainWindow()
    window.show()
    sys.exit(app.exec())