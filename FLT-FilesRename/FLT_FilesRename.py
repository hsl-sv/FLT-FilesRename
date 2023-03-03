import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QFile, QIODevice

from manager import RenameManager

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui_file_name = "FLT_FilesRename.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    # Connect here
    dirmanager = RenameManager(window)

    window.btn_folder.clicked.connect(dirmanager.opendialog)

    window.tbx_replace_target.textChanged.connect(dirmanager.replace_changed)
    window.tbx_replace_dest.textChanged.connect(dirmanager.replace_preview)
    window.btn_apply.clicked.connect(dirmanager.replace_apply)

    # Show
    window.show()

    sys.exit(app.exec())