import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QTextBrowser, QDialog, QVBoxLayout

import zipfile
import winreg

def get_onedrive_path():
    try:
        # Try to get the OneDrive path for the current user
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\OneDrive") as key:
            onedrive_path = winreg.QueryValueEx(key, "UserFolder")[0]
            return onedrive_path
    except Exception:
        return None


class ModManager(QWidget):
    def __init__(self):
        super().__init__()

        # Check default directory
        self.game_dir = os.path.expanduser('~/Documents/My Games/Galciv4')
        
        # If not found, check OneDrive directory
        if not os.path.exists(self.game_dir):
            onedrive_path = get_onedrive_path()
            if onedrive_path:
                self.game_dir = os.path.join(onedrive_path, 'Documents/My Games/Galciv4')

        if not os.path.exists(self.game_dir):
            QMessageBox.critical(self, 'Error', 'The Galciv4 directory was not found in Documents/My Games or OneDrive/Documents/My Games.')
            return

        self.active_mods_dir = os.path.join(self.game_dir, 'mods')
        self.inactive_mods_dir = os.path.join(self.game_dir, 'inactivemods')

        # Instantiate QVBoxLayout
        self.layout = QVBoxLayout()
        
        # Ensure directories exist
        self.ensure_directory_exists(self.active_mods_dir)
        self.ensure_directory_exists(self.inactive_mods_dir)

        # Layout for lists
        self.list_layout = QHBoxLayout()

        # Layout for Active mods list and its label
        self.active_mods_layout = QVBoxLayout()        
        self.active_mods_layout.addWidget(QLabel('Active Mods'))
        self.active_mods_list = QListWidget()
        self.active_mods_layout.addWidget(self.active_mods_list)
        self.list_layout.addLayout(self.active_mods_layout)

        # Layout for Inactive mods list and its label
        self.inactive_mods_layout = QVBoxLayout()
        self.inactive_mods_layout.addWidget(QLabel('Inactive Mods'))
        self.inactive_mods_list = QListWidget()
        self.inactive_mods_layout.addWidget(self.inactive_mods_list)
        self.list_layout.addLayout(self.inactive_mods_layout)


        # Button to activate/deactivate
        self.btn_activate = QPushButton('Activate Mod')
        self.btn_activate.clicked.connect(self.activate_mod)
        self.btn_deactivate = QPushButton('Deactivate Mod')
        self.btn_deactivate.clicked.connect(self.deactivate_mod)

        # Add widgets to main layout
        self.layout.addLayout(self.list_layout)
        self.layout.addWidget(self.btn_activate)
        self.layout.addWidget(self.btn_deactivate)

        self.btn_add_mod = QPushButton('Add Mod')
        self.btn_add_mod.clicked.connect(self.add_mod)
        self.layout.addWidget(self.btn_add_mod)

        self.btn_get_info = QPushButton('Get Info')
        self.btn_get_info.clicked.connect(self.get_info)
        self.layout.addWidget(self.btn_get_info)

        self.btn_open_directory = QPushButton('Open Folder')
        self.btn_open_directory.clicked.connect(self.open_directory)
        self.layout.addWidget(self.btn_open_directory)

         # Connect itemClicked signals to clear selection in the opposing list
        self.active_mods_list.itemClicked.connect(self.clear_inactive_selection)
        self.inactive_mods_list.itemClicked.connect(self.clear_active_selection)



        # Refresh lists
        self.refresh_lists()

        self.setLayout(self.layout)
        self.setWindowTitle('Galciv4 Mod Manager')
        self.show()

    # Methods to clear selections
    def clear_active_selection(self):
        self.active_mods_list.clearSelection()

    def clear_inactive_selection(self):
        self.inactive_mods_list.clearSelection()

    def open_directory(self):
        os.startfile(self.game_dir)

    def add_mod(self):

        downloads_dir = os.path.expanduser('~/Downloads')

        # Show a file dialog to select the ZIP file
        zip_file_path, _ = QFileDialog.getOpenFileName(self, "Select Mod ZIP File", downloads_dir, "ZIP Files (*.zip)")


        # Check if user cancelled the file dialog
        if not zip_file_path:
            return

        # Extract the ZIP file to the inactive mods directory
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Extract all the contents into the inactive_mods_dir
            zip_ref.extractall(self.inactive_mods_dir)

        # Refresh the list of mods
        self.refresh_lists()

    def ensure_directory_exists(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to create directory {directory}. Error: {str(e)}')

    def refresh_lists(self):
        # Populate active mods list
        self.active_mods_list.clear()
        for mod in os.listdir(self.active_mods_dir):
            if os.path.isdir(os.path.join(self.active_mods_dir, mod)) and mod.lower() not in [item.text().lower() for item in self.active_mods_list.findItems("*", Qt.MatchWildcard)]:
                self.active_mods_list.addItem(mod)

        # Populate inactive mods list
        self.inactive_mods_list.clear()
        for mod in os.listdir(self.inactive_mods_dir):
            if os.path.isdir(os.path.join(self.inactive_mods_dir, mod)) and mod.lower() not in [item.text().lower() for item in self.inactive_mods_list.findItems("*", Qt.MatchWildcard)]:
                self.inactive_mods_list.addItem(mod)

    def activate_mod(self):
        current_item = self.inactive_mods_list.currentItem()
        if current_item:
            mod_name = current_item.text()
            if not any(existing_mod.lower() == mod_name.lower() for existing_mod in os.listdir(self.active_mods_dir)):
                shutil.move(os.path.join(self.inactive_mods_dir, mod_name), os.path.join(self.active_mods_dir, mod_name))
                self.refresh_lists()

    def deactivate_mod(self):
        current_item = self.active_mods_list.currentItem()
        if current_item:
            mod_name = current_item.text()
            if not any(existing_mod.lower() == mod_name.lower() for existing_mod in os.listdir(self.inactive_mods_dir)):
                shutil.move(os.path.join(self.active_mods_dir, mod_name), os.path.join(self.inactive_mods_dir, mod_name))
                self.refresh_lists()

    def get_info(self):
        # Determine the selected item from both lists
        active_selected_items = self.active_mods_list.selectedItems()
        inactive_selected_items = self.inactive_mods_list.selectedItems()

        # Find out which list the user has selected an item from
        if active_selected_items:
            mod_dir = self.active_mods_dir
            mod_name = active_selected_items[0].text()
        elif inactive_selected_items:
            mod_dir = self.inactive_mods_dir
            mod_name = inactive_selected_items[0].text()
        else:
            return

        # Rest of your code remains the same
        readme_path = next((os.path.join(mod_dir, mod_name, file) for file in os.listdir(os.path.join(mod_dir, mod_name)) if file.lower() == "readme.html"), None)

        if readme_path and os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            self.show_readme_dialog(html_content)
        else:
            QMessageBox.information(self, 'Info', 'No Readme.html file found for the selected mod.')





    def show_readme_dialog(self, html_content):
        dialog = QDialog(self)
        dialog.setWindowTitle("Mod Information")
        dialog.setFixedSize(800, 240)
        layout = QVBoxLayout()
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)  # To open external links in a web browser
        text_browser.setHtml(html_content)

        layout.addWidget(text_browser)
        
        dialog.setLayout(layout)
        dialog.exec_()

            

# ...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ModManager()
    sys.exit(app.exec_())
