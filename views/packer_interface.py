# views/packer_interface.py
import os
import json
import zipfile
import tempfile
import shutil
from datetime import datetime

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QApplication
from qfluentwidgets import (CaptionLabel, StrongBodyLabel, TitleLabel, PrimaryPushButton, PushButton, 
                            LineEdit, TextEdit, CardWidget)

from i18n import tr

class PackerInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("PackerInterface")
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 25, 30, 25)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(tr("packer_title"), self)
        self.main_layout.addWidget(self.title_label)

        self.config_card = CardWidget(self)
        card_layout = QVBoxLayout(self.config_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        # Config 1
        self.lbl_json = StrongBodyLabel(tr("host_json_label"))
        card_layout.addWidget(self.lbl_json)
        json_layout = QHBoxLayout()
        self.txt_json = LineEdit(self)
        self.txt_json.setPlaceholderText(tr("host_json_ph"))
        self.btn_json = PushButton(tr("btn_browse"), self)
        self.btn_json.clicked.connect(self.browse_host_json)
        json_layout.addWidget(self.txt_json)
        json_layout.addWidget(self.btn_json)
        card_layout.addLayout(json_layout)

        # Config 2
        self.lbl_bin = StrongBodyLabel(tr("plugin_bin_label"))
        card_layout.addWidget(self.lbl_bin)
        bin_layout = QHBoxLayout()
        self.txt_bin = LineEdit(self)
        self.txt_bin.setPlaceholderText(tr("plugin_bin_ph"))
        self.btn_bin = PushButton(tr("btn_browse"), self)
        self.btn_bin.clicked.connect(self.browse_plugin_bin)
        bin_layout.addWidget(self.txt_bin)
        bin_layout.addWidget(self.btn_bin)
        card_layout.addLayout(bin_layout)

        # Config 3
        self.lbl_out = StrongBodyLabel(tr("dist_out_label"))
        card_layout.addWidget(self.lbl_out)
        out_layout = QHBoxLayout()
        self.txt_out = LineEdit(self)
        self.txt_out.setPlaceholderText(tr("dist_out_ph"))
        self.btn_out = PushButton(tr("btn_browse"), self)
        self.btn_out.clicked.connect(self.browse_output_dir)
        out_layout.addWidget(self.txt_out)
        out_layout.addWidget(self.btn_out)
        card_layout.addLayout(out_layout)

        self.main_layout.addWidget(self.config_card)

        # Log Area
        self.log_card = CardWidget(self)
        log_layout = QVBoxLayout(self.log_card)
        log_layout.setContentsMargins(15, 15, 15, 15)
        
        self.lbl_log = CaptionLabel(tr("log_label"))
        log_layout.addWidget(self.lbl_log)
        self.log_area = TextEdit(self)
        self.log_area.setReadOnly(True)
        font = QFont("Consolas", 10)
        self.log_area.setFont(font)
        log_layout.addWidget(self.log_area)
        
        self.main_layout.addWidget(self.log_card, stretch=1)

        # Action Button
        self.action_btn = PrimaryPushButton(tr("btn_pack"), self)
        self.action_btn.setFixedHeight(42)
        self.action_btn.clicked.connect(self.start_packing)
        self.main_layout.addWidget(self.action_btn)

    def update_texts(self):
        """响应语言切换，刷新界面文本"""
        self.title_label.setText(tr("packer_title"))
        self.lbl_json.setText(tr("host_json_label"))
        self.txt_json.setPlaceholderText(tr("host_json_ph"))
        self.btn_json.setText(tr("btn_browse"))
        self.lbl_bin.setText(tr("plugin_bin_label"))
        self.txt_bin.setPlaceholderText(tr("plugin_bin_ph"))
        self.btn_bin.setText(tr("btn_browse"))
        self.lbl_out.setText(tr("dist_out_label"))
        self.txt_out.setPlaceholderText(tr("dist_out_ph"))
        self.btn_out.setText(tr("btn_browse"))
        self.lbl_log.setText(tr("log_label"))
        self.action_btn.setText(tr("btn_pack"))

    def browse_host_json(self):
        current_path = self.txt_json.text().strip()
        start_dir = os.path.dirname(current_path) if os.path.isfile(current_path) else current_path
        start_dir = start_dir if os.path.exists(start_dir) else ""
        path, _ = QFileDialog.getOpenFileName(self, "Host JSON", start_dir, "JSON Files (*.json);;All Files (*)")
        if path: 
            self.txt_json.setText(os.path.normpath(path))

    def browse_plugin_bin(self):
        current_path = self.txt_bin.text().strip()
        start_dir = current_path if os.path.isdir(current_path) else ""
        path = QFileDialog.getExistingDirectory(self, "Plugin Bin", start_dir)
        if path: 
            self.txt_bin.setText(os.path.normpath(path))

    def browse_output_dir(self):
        current_path = self.txt_out.text().strip()
        start_dir = current_path if os.path.isdir(current_path) else ""
        path = QFileDialog.getExistingDirectory(self, "Dist Output", start_dir)
        if path: 
            self.txt_out.setText(os.path.normpath(path))

    def log(self, message, prefix="INFO"):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{time_str}] [{prefix}] {message}")
        self.log_area.ensureCursorVisible()
        QApplication.processEvents()

    def start_packing(self):
        json_path = self.txt_json.text().strip()
        bin_dir = self.txt_bin.text().strip()
        out_dir = self.txt_out.text().strip()

        if not json_path or not bin_dir or not out_dir:
            QMessageBox.critical(self, tr("msg_missing_title"), tr("msg_missing_text"))
            return

        if not os.path.exists(json_path) or not os.path.exists(bin_dir):
            QMessageBox.critical(self, tr("msg_path_title"), tr("msg_path_text"))
            return

        self.log_area.clear()
        self.log(tr("log_start"), "START")

        def extract_dlls(obj, out_set):
            if isinstance(obj, str) and obj.lower().endswith('.dll'):
                out_set.add(os.path.basename(obj).lower())
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(k, str) and k.lower().endswith('.dll'):
                        out_set.add(os.path.basename(k).lower())
                    extract_dlls(v, out_set)
            elif isinstance(obj, list):
                for item in obj: extract_dlls(item, out_set)

        host_assemblies = set()
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                extract_dlls(json.load(f), host_assemblies)
            self.log(tr("log_host_success").format(len(host_assemblies)))
        except Exception as e:
            self.log(tr("log_host_warn").format(str(e)), "WARN")

        plugin_deps_json = next((os.path.join(bin_dir, f) for f in os.listdir(bin_dir) if f.endswith('.deps.json')), None)
        plugin_assemblies = set()
        use_strict_mode = False

        if plugin_deps_json:
            try:
                with open(plugin_deps_json, 'r', encoding='utf-8') as f:
                    extract_dlls(json.load(f), plugin_assemblies)
                self.log(tr("log_strict_mode").format(os.path.basename(plugin_deps_json)))
                use_strict_mode = True
            except Exception as e:
                self.log(tr("log_strict_fail").format(str(e)), "WARN")

        keep_assemblies = set()
        if use_strict_mode:
            keep_assemblies = plugin_assemblies - host_assemblies
            self.log(tr("log_strict_calc").format(len(keep_assemblies)))

        plugin_dll = next((f for f in os.listdir(bin_dir) if f.endswith('.dll') and not 'Core' in f and not 'DevTools' in f), None)
        plugin_name = os.path.splitext(plugin_dll)[0] if plugin_dll else "Plugin"
        blp_filename = f"{plugin_name}.v1.0.0.blp"
        final_blp_path = os.path.join(out_dir, blp_filename)

        trim_count, copy_count = 0, 0

        with tempfile.TemporaryDirectory() as staging_dir:
            for root_dir, _, files in os.walk(bin_dir):
                for file in files:
                    file_lower = file.lower()
                    file_path = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(file_path, bin_dir)

                    is_trimmed = False
                    if file_lower.endswith('.dll'):
                        if use_strict_mode:
                            if file_lower not in keep_assemblies and file_lower != plugin_dll.lower():
                                is_trimmed = True
                        else:
                            if file_lower in host_assemblies or file_lower == 'betterlyrics.core.dll':
                                is_trimmed = True

                    if is_trimmed:
                        self.log(tr("log_trim").format(rel_path))
                        trim_count += 1
                        continue
                    
                    if any(x in file_lower for x in ["_trimmingconfig", "_trimmerroots", ".pdb"]):
                        continue

                    dest_path = os.path.join(staging_dir, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                    copy_count += 1

            if copy_count == 0:
                self.log(tr("log_err_no_dll"), "ERROR")
                return

            os.makedirs(out_dir, exist_ok=True)
            with zipfile.ZipFile(final_blp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root_dir, _, files in os.walk(staging_dir):
                    for file in files:
                        fp = os.path.join(root_dir, file)
                        zipf.write(fp, os.path.relpath(fp, staging_dir))

        self.log("==================================================", "END")
        self.log(tr("log_end_1"))
        self.log(tr("log_end_2").format(trim_count))
        self.log(tr("log_end_3").format(final_blp_path))
        
        QMessageBox.information(self, tr("msg_success_title"), tr("msg_success_text").format(blp_filename))