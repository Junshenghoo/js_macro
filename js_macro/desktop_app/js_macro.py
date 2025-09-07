import sys
import json
import win32api
import keyboard
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QSpacerItem,
    QSizePolicy, QInputDialog, QDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer

current_key =0

def find_circuitpy_drive(label="CIRCUITPY"):
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    for d in drives:
        try:
            vol_label = win32api.GetVolumeInformation(d)[0]
            if vol_label.upper() == label:
                return d
        except:
            continue
    return None

class KeypadDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.active_key_name = None
        self.mode = 1
        self.mode_name, self.keys_dict, self.max_mode = self.read_config()

        self.setWindowTitle("JS Macro Keyboard")

        # Main vertical layout
        main_layout = QVBoxLayout(self)

        # -----------------------------
        # Middle: Keypad container
        # -----------------------------
        self.image_container = QWidget(self)
        self.label = QLabel(self.image_container)

        pixmap = QPixmap("macro.png")
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.width(), pixmap.height())
        self.image_container.setFixedSize(pixmap.size())

        main_layout.addWidget(
            self.image_container,
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        )

        # Transparent buttons on keypad
        self.create_button("Mode", 40, 50, 85, 85)
        self.create_button("7", 40, 150, 85, 85)
        self.create_button("8", 145, 150, 85, 85)
        self.create_button("9", 250, 150, 85, 85)
        self.create_button("4", 40, 245, 85, 85)
        self.create_button("5", 145, 245, 85, 85)
        self.create_button("6", 250, 245, 85, 85)
        self.create_button("1", 40, 340, 85, 85)
        self.create_button("2", 145, 340, 85, 85)
        self.create_button("3", 250, 340, 85, 85)

        # -----------------------------
        # Bottom: Str + text box
        # -----------------------------
        bottom_frame = QFrame(self)
        bottom_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.bottom_layout = QVBoxLayout(bottom_frame)  # store as self.bottom_layout

        self.bottom_title = QLabel(f"Mode: {self.mode_name}\nButton: None")
        self.bottom_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.bottom_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.bottom_layout.addWidget(self.bottom_title) 

        # ---- top-right buttons ----
        btn_row = QHBoxLayout()
        btn_row.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_rename = QPushButton("Rename")
        self.btn_rename.clicked.connect(self.rename)
        self.btn_add_mode = QPushButton("+ Mode")
        self.btn_add_mode.clicked.connect(self.add_mode)
        self.btn_del_mode = QPushButton("- Mode")
        self.btn_del_mode.clicked.connect(self.delete_mode)
        self.btn_add_str = QPushButton("+ String")
        #self.btn_add_str.clicked.connect(self.add_string_row) 
        self.btn_add_cmd = QPushButton("+ CMD")
        #self.btn_add_cmd.clicked.connect(self.add_cmd_row)
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_rows)
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_last_row)
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_all_rows)

        self.btn_add_str.clicked.connect(lambda: self.add_string_row())
        self.btn_add_cmd.clicked.connect(lambda: self.add_cmd_row())

        btn_row.addWidget(self.btn_rename)
        btn_row.addWidget(self.btn_add_mode)
        btn_row.addWidget(self.btn_del_mode)
        btn_row.addWidget(self.btn_add_str)
        btn_row.addWidget(self.btn_add_cmd)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_clear)

        self.bottom_layout.addLayout(btn_row)

        self.rows = []        
        self.str_count = 0
        self.cmd_count = 0

        self.bottom_layout.addStretch()
        main_layout.addWidget(bottom_frame)

        # Resize window larger than image
        self.resize(pixmap.width() + 400, pixmap.height() + 400)

    def create_button(self, text, x, y, w, h):
        btn = QPushButton("", self.image_container)
        btn.setGeometry(x, y, w, h)
        btn.setStyleSheet("background: transparent; border: none;")
        btn.clicked.connect(lambda _, t=text: self.on_click(t))

    def on_click(self, key):
        print(f"Button {key} pressed!")
        
        if key == "Mode":
            self.mode += 1
            if self.mode > self.max_mode:
                self.mode = 1
            self.mode_name, self.keys_dict, self.max_mode = self.read_config()
            self.bottom_title.setText(f"Mode: {self.mode_name}\nButton: None")
            self.active_key_name = None 
            self.clear_all_rows()
            return

        # For number keys
        self.active_key_name = f"key_{key}"
        self.bottom_title.setText(f"Mode: {self.mode_name}\nButton: {key}")
        self.clear_all_rows()
        current_key = key
        
        key_name = f"key_{key}"
        if key_name in self.keys_dict:
            data_list = self.keys_dict[key_name]
            for data in data_list:
                if "cmd" in data:
                    self.add_cmd_row(", ".join(map(str, data["cmd"])))
                if "str" in data:
                    self.add_string_row(str(data["str"]))
                    
    def rename(self):
        new_name, ok = QInputDialog.getText(self, "Rename Mode", "Enter new mode name:")

        if ok and new_name.strip():  # if user clicked OK and input is not empty
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)

            mode_key = f"mode{self.mode}"
            if mode_key in data:
                data[mode_key]["name"] = new_name

                # Save back
                with open(CONFIG_PATH, "w") as f:
                    json.dump(data, f, indent=4)

                # Update UI
                mode_name = new_name
                self.bottom_title.setText(f"Mode: {mode_name}\nButton: None")
                print(f"Mode {mode_key} renamed to '{new_name}'")
            else:
                print(f"{mode_key} not found in config")

    def add_mode(self):
    # Read config
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)

        # Shift all modes after current mode
        mode_keys = sorted(
            [k for k in data.keys() if k.startswith("mode") and k[4:].isdigit()],
            key=lambda x: int(x[4:]),
            reverse=True
        )
        for key in mode_keys:
            num = int(key[4:])
            if num > self.mode:
                data[f"mode{num+1}"] = data.pop(key)

        # Add new mode after current mode
        new_mode_num = self.mode + 1
        new_mode_key = f"mode{new_mode_num}"
        data[new_mode_key] = {"name": f"Mode {new_mode_num}", "keys": []}

        # Sort data numerically by mode
        sorted_data = dict(sorted(
            data.items(),
            key=lambda x: int(x[0][4:]) if x[0].startswith("mode") else x[0]
        ))

        # Save back
        with open(CONFIG_PATH, "w") as f:
            json.dump(sorted_data, f, indent=4)

        # Update max_mode and switch to the new mode
        self.max_mode = max([int(k[4:]) for k in sorted_data.keys() if k.startswith("mode")])
        self.mode = new_mode_num
        self.mode_name, self.keys_dict, self.max_mode = self.read_config()
        self.bottom_title.setText(f"Mode: {self.mode_name}\nButton: None")
        self.active_key_name = None
        self.clear_all_rows()
        self.rename()
        print(f"Added {new_mode_key} and switched to it.")

    def delete_mode(self):
        if self.mode == 1:
            print("Cannot delete mode1")
            return

        # Read config
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)

        mode_key = f"mode{self.mode}"

        if mode_key in data:
            # Remove the current mode
            del data[mode_key]
            print(f"Deleted {mode_key}")

            # Shift all higher-numbered modes down by 1
            mode_keys = sorted([k for k in data.keys() if k.startswith("mode") and k[4:].isdigit()],
                            key=lambda x: int(x[4:]))
            for key in mode_keys:
                num = int(key[4:])
                if num > self.mode:
                    data[f"mode{num-1}"] = data.pop(key)

            # Save back
            with open(CONFIG_PATH, "w") as f:
                json.dump(data, f, indent=4)

            # Switch to previous mode
            self.mode -= 1
            self.mode_name, self.keys_dict, self.max_mode = self.read_config()
            self.bottom_title.setText(f"Mode: {self.mode_name}\nButton: None")
            self.active_key_name = None
            self.clear_all_rows()
        else:
            print(f"{mode_key} not found")

    def add_string_row(self, text = ""):
        if not self.active_key_name:
            print("Select a key first")
            return
        self.str_count += 1
        str_row = QHBoxLayout()
        label_str = QLabel(f"Str    :")
        text_input = QLineEdit()
        text_input.setText(text) 

        str_row.addWidget(label_str)
        str_row.addWidget(text_input)

        self.bottom_layout.insertLayout(self.bottom_layout.count() - 1, str_row)
        self.rows.append((str_row, "str"))   # keep reference + type

    def add_cmd_row(self, text=""):
        if not self.active_key_name:
            print("Select a key first")
            return

        self.cmd_count += 1
        cmd_row = QHBoxLayout()

        # Label "CMD:"
        label_title = QLabel("CMD:")
        cmd_row.addWidget(label_title)

        # Frame to mimic a text box
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                background-color: white;
                border-radius: 3px;
            }
        """)
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(5, 2, 5, 2)

        # Label inside frame to show CMD
        label_cmd = QLabel(text)
        label_cmd.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        frame_layout.addWidget(label_cmd)

        cmd_row.addWidget(frame, stretch=1)
        cmd_row.addStretch()

        # ---- CHANGE BUTTON ----
        btn_change = QPushButton("Change")
        cmd_row.addWidget(btn_change)

        def change_cmd():
            dialog = CaptureDialog(self, label_cmd)
            dialog.exec()

        btn_change.clicked.connect(change_cmd)

        # Insert row into layout
        self.bottom_layout.insertLayout(self.bottom_layout.count() - 1, cmd_row)
        self.rows.append((cmd_row, "cmd"))   # mark as cmd row

    def delete_last_row(self):

        if not self.rows:
            return

        row, row_type = self.rows.pop()  # get last added row

        # remove widgets inside row
        while row.count():
            item = row.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def clear_all_rows(self):
        while self.rows:
            row, row_type = self.rows.pop()

            # remove widgets inside each row
            while row.count():
                item = row.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def save_rows(self):
        if not self.active_key_name:
            print("No active key selected")
            return

        data_list = []
        for row, row_type in self.rows:
            if row_type == "cmd":
                # The frame is at index 1 in the row
                frame = row.itemAt(1).widget()
                if frame and isinstance(frame, QFrame):
                    label = frame.layout().itemAt(0).widget()  # first widget inside frame
                    if label and isinstance(label, QLabel):
                        data_list.append({"cmd": [s.strip() for s in label.text().split(",")]})
            elif row_type == "str":
                # text rows still use QLineEdit
                for i in range(row.count()):
                    widget = row.itemAt(i).widget()
                    if isinstance(widget, QLineEdit):
                        data_list.append({"str": widget.text()})

        # Read JSON, update, then write back
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)

        mode_key = f"mode{self.mode}"
        keys_list = data[mode_key].get("keys", [])

        # Update or add key
        for k in keys_list:
            if self.active_key_name in k:
                k[self.active_key_name] = data_list
                break
        else:
            keys_list.append({self.active_key_name: data_list})

        data[mode_key]["keys"] = keys_list

        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Saved {self.active_key_name}:", data_list)
        self.mode_name, self.keys_dict, self.max_mode = self.read_config()
        number_only = self.active_key_name.replace("key_", "")
        self.bottom_title.setText(f"Mode: {self.mode_name}\nButton: {number_only}")

    def read_config(self):
        with open(CONFIG_PATH, "r") as file:
            data = json.load(file)

        # Sort mode keys numerically
        sorted_modes = sorted(
            [k for k in data.keys() if k.startswith("mode") and k[4:].isdigit()],
            key=lambda x: int(x[4:])
        )
        max_mode = max([int(k[4:]) for k in sorted_modes]) if sorted_modes else 1

        # Get current mode data
        mode_key = f"mode{self.mode}"
        mode_data = data.get(mode_key, {"name": f"Mode {self.mode}", "keys": []})
        mode_name = mode_data.get("name", f"Mode {self.mode}")
        self.keys_dict = {list(d.keys())[0]: list(d.values())[0] for d in mode_data.get("keys", [])}

        print(f"Mode name: {mode_name}")
        for key, value in self.keys_dict.items():
            print(f"{key} data:", value)

        return mode_name, self.keys_dict, max_mode
    
    def write_config(self, mode, key_name, data_list):
        # 1. Read existing data
        with open(CONFIG_PATH, "r") as file:
            data = json.load(file)
        
        # 2. Update the specific mode/key
        mode_key = f"mode{mode}"
        if mode_key not in data:
            data[mode_key] = {"name": f"Mode {mode}", "keys": []}

        # Find the key in keys list
        keys_list = data[mode_key].get("keys", [])
        updated = False
        for k in keys_list:
            if key_name in k:
                k[key_name] = data_list
                updated = True
                break
        if not updated:
            keys_list.append({key_name: data_list})

        data[mode_key]["keys"] = keys_list

        # 3. Write back
        with open(CONFIG_PATH, "w") as file:
            json.dump(data, file, indent=4)

class CaptureDialog(QDialog):
    def __init__(self, parent=None, label_cmd=None):
        super().__init__(parent)
        self.setWindowTitle("Press your key combination")
        self.captured_keys = []
        self.label_cmd = label_cmd

        layout = QVBoxLayout(self)
        self.info_label = QLabel("Press keys...", self)
        layout.addWidget(self.info_label)

        # Hook keyboard
        self.hook_handle = keyboard.on_press(self.on_key)

        # Update label with captured keys
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_label)
        self.timer.start(50)

        # OK button (mouse-click only, no Enter/Space trigger)
        btn_ok = QPushButton("OK", self)
        btn_ok.setAutoDefault(False)
        btn_ok.setDefault(False)
        btn_ok.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_ok.clicked.connect(self.finish)
        layout.addWidget(btn_ok)

    def on_key(self, event):
        key_name = event.name.upper()
        if key_name == "CAPS LOCK":
            key_name = "CAPS_LOCK"
        if key_name == "ESC":
            key_name = "ESCAPE"
        if key_name == "PRINT SCREEN":
            key_name = "PRINT_SCREEN"
        if key_name == "PAGE UP":
            key_name = "PAGE_UP"
        if key_name == "PAGE DOWN":
            key_name = "PAGE_DOWN"
        if key_name == "LEFT":
            key_name = "LEFT_ARROW"
        if key_name == "UP":
            key_name = "UP_ARROW"
        if key_name == "RIGHT":
            key_name = "RIGHT_ARROW"
        if key_name == "DOWN":
            key_name = "DOWN_ARROW"
        if key_name == "NUM LOCK":
            key_name = "KEYPAD_NUMLOCK"
        if "WINDOWS" in  key_name:
            key_name = "WINDOWS"
        if key_name not in self.captured_keys:
            self.captured_keys.append(key_name)

    def update_label(self):
        self.info_label.setText("Keys captured: " + ", ".join(self.captured_keys))

    def finish(self):
        self.timer.stop()
        keyboard.unhook(self.hook_handle)
        if self.captured_keys and self.label_cmd:
            self.label_cmd.setText(", ".join(self.captured_keys))
        self.accept()

    # override keyPressEvent to swallow Enter, Escape, Space
    def keyPressEvent(self, event):
        try:  # PyQt6
            keys_block = (
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
                Qt.Key.Key_Escape,
                Qt.Key.Key_Space,
            )
        except AttributeError:  # PyQt5 fallback
            keys_block = (
                Qt.Key_Return,
                Qt.Key_Enter,
                Qt.Key_Escape,
                Qt.Key_Space,
            )

        if event.key() in keys_block:
            event.ignore()   # do nothing
            return
        super().keyPressEvent(event)


if __name__ == "__main__":
    circuitpy_drive = find_circuitpy_drive()
    if circuitpy_drive:
        CONFIG_PATH = circuitpy_drive + "config.json"
        print("Found CIRCUITPY at:", CONFIG_PATH)
    else:
        # Show "not found" image
        app = QApplication(sys.argv)
        msg_window = QWidget()
        msg_window.setWindowTitle("Macro Not Found")
        layout = QVBoxLayout(msg_window)
        label = QLabel()
        pixmap = QPixmap("not_found.png")
        label.setPixmap(pixmap)
        layout.addWidget(label)
        QTimer.singleShot(2000, msg_window.close)
        msg_window.show()
        sys.exit(app.exec())
    app = QApplication(sys.argv)
    window = KeypadDemo()
    window.show()
    sys.exit(app.exec())