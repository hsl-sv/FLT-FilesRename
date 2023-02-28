import os
import copy
import glob

from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QStandardItem, QStandardItemModel, QBrush, QColor

class RenameManager(object):
    
    def __init__(self, MainWindow):
        super().__init__()
        self.cwd = os.getcwd()
        self.cwd_filelist = []
        self.cwd_filelist_preview = []
        self.items = QStandardItemModel()
        self.items_preview = QStandardItemModel()
        self.brush_selected = QBrush(QColor(0, 0, 255))
        self.MainWindow = MainWindow

    def test(self):
        print("Qt Connect Test")

    def opendialog(self):
        
        folder = QFileDialog.getExistingDirectory(None, "Select Directory", self.cwd)
        self.cwd = folder
        self.populate_listview(self.cwd)

    def populate_listview(self, folder):
        flist = glob.glob(f"{str(folder)}" + os.sep + "*")
        dirlist = []
        self.items.clear()

        for i, fpath in enumerate(flist):
            if os.path.isdir(fpath):
                dirlist.append(i)
            else:
                self.items.appendRow(QStandardItem(os.path.basename(fpath)))
                self.items_preview.appendRow(QStandardItem(os.path.basename(fpath)))
        
        dirlist = dirlist[::-1]
        for j in range(len(dirlist)):
            del flist[dirlist[j]]

        self.cwd_filelist = flist
        self.cwd_filelist_preview = copy.copy(self.cwd_filelist)

        self.MainWindow.lv_directory.setModel(self.items)
        self.MainWindow.lv_preview.setModel(self.items)
        self.MainWindow.lbl_currentdir.setText(str(folder))

    def replace_changed(self):

        target_txt = self.MainWindow.tbx_replace_target.toPlainText()
        model = self.MainWindow.lv_directory.model()

        for i in range(model.rowCount()):
            if target_txt in model.item(i).text():
                model.item(i).setForeground(self.brush_selected)

        print(self.MainWindow.tbx_replace_target.toPlainText())
        pass