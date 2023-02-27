import os
import glob

from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QStandardItem, QStandardItemModel

class loaddir(object):
    
    def __init__(self, MainWindow):
        super().__init__()
        self.cwd = os.getcwd()
        self.items = QStandardItemModel()
        self.MainWindow = MainWindow

    def test(self):
        print("Qt Connect Test")

    def opendialog(self):
        
        folder = QFileDialog.getExistingDirectory(None, "Select Directory", self.cwd)
        self.cwd = folder
        self.populate_listview(self.cwd)

    def populate_listview(self, folder):
        flist = glob.glob(f"{str(folder)}" + os.sep + "*")
        
        self.items.clear()

        for i, fpath in enumerate(flist):
            self.items.appendRow(QStandardItem(fpath))

        self.MainWindow.lv_directory.setModel(self.items)