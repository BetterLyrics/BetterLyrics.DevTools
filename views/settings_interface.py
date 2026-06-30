# views/settings_interface.py
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, CardWidget, StrongBodyLabel, ComboBox, setTheme, Theme

from i18n import tr, set_lang, get_lang

class SettingsInterface(QWidget):
    langChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingsInterface")
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 25, 30, 25)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(tr("settings_title"), self)
        self.main_layout.addWidget(self.title_label)

        # 主题设置
        self.theme_card = CardWidget(self)
        theme_layout = QHBoxLayout(self.theme_card)
        theme_layout.setContentsMargins(20, 15, 20, 15)
        self.lbl_theme = StrongBodyLabel(tr("theme_label"), self)
        self.combo_theme = ComboBox(self)
        self.combo_theme.addItems([tr("theme_dark"), tr("theme_light")])
        self.combo_theme.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.lbl_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.combo_theme)
        self.main_layout.addWidget(self.theme_card)

        # 语言设置
        self.lang_card = CardWidget(self)
        lang_layout = QHBoxLayout(self.lang_card)
        lang_layout.setContentsMargins(20, 15, 20, 15)
        self.lbl_lang = StrongBodyLabel(tr("lang_label"), self)
        self.combo_lang = ComboBox(self)
        self.combo_lang.addItems(["简体中文", "English"])
        self.combo_lang.setCurrentIndex(0 if get_lang() == "zh" else 1)
        self.combo_lang.currentIndexChanged.connect(self.on_lang_changed)
        lang_layout.addWidget(self.lbl_lang)
        lang_layout.addStretch()
        lang_layout.addWidget(self.combo_lang)
        self.main_layout.addWidget(self.lang_card)

        self.main_layout.addStretch()

    def update_texts(self):
        self.title_label.setText(tr("settings_title"))
        self.lbl_theme.setText(tr("theme_label"))
        self.combo_theme.setItemText(0, tr("theme_dark"))
        self.combo_theme.setItemText(1, tr("theme_light"))
        self.lbl_lang.setText(tr("lang_label"))

    def on_theme_changed(self, idx):
        setTheme(Theme.DARK if idx == 0 else Theme.LIGHT)

    def on_lang_changed(self, idx):
        set_lang("zh" if idx == 0 else "en")
        self.langChanged.emit()