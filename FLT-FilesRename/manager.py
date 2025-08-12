import os
import copy
import glob
import datetime
import re

from PySide6.QtWidgets import QFileDialog, QMessageBox
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
        self.brush_unselect = QBrush(QColor(0, 0, 0))
        self.brush_preview = QBrush(QColor(255, 0, 0))
        self.MainWindow = MainWindow

    def test(self):

        print("Test function")

    def _lenci(self, ci):
        return sum(1 for _ in ci)

    def opendialog(self):
        
        folder = QFileDialog.getExistingDirectory(None, "Select Directory", self.cwd)
        self.cwd = folder
        self.populate_listview(self.cwd)

    def wordwrap_clicked(self):
        self.replace_changed()
        self.replace_preview()

    def populate_listview(self, folder):
        if self.MainWindow.cbx_recursive.isChecked():
            flist = glob.glob(f"{str(folder)}" + os.sep + "**" + os.sep + "*", recursive=True)
        else:
            flist = glob.glob(f"{str(folder)}" + os.sep + "*")
        dirlist = []
        self.items.clear()
        self.items_preview.clear()

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
        self.MainWindow.lv_preview.setModel(self.items_preview)
        self.MainWindow.lbl_currentdir.setText(str(folder))

    def replace_changed(self):

        target_txt = self.MainWindow.tbx_replace_target.toPlainText()
        model = self.MainWindow.lv_directory.model()
        pattern = re.compile(rf"{target_txt}")

        if not target_txt or target_txt.isspace():            
            self.populate_listview(self.cwd)
            return

        if model:
            for i in range(model.rowCount()):
                if not self.MainWindow.cbx_wordwrap.isChecked():
                    if target_txt in model.item(i).text():
                        model.item(i).setForeground(self.brush_selected)
                    else:
                        model.item(i).setForeground(self.brush_unselect)
                else:
                    matches = pattern.finditer(model.item(i).text())
                    if self._lenci(matches) > 0:
                        model.item(i).setForeground(self.brush_selected)
                    else:
                        model.item(i).setForeground(self.brush_unselect)

    def replace_preview(self):
        # tbx_replace_dest -> preview model
        rtarget = self.MainWindow.tbx_replace_target.toPlainText()
        rdest = self.MainWindow.tbx_replace_dest.toPlainText()

        if not rtarget or rtarget.isspace():
            self.replace_changed()
            return
        
        pmodel = self.MainWindow.lv_preview.model()
        plist = self.cwd_filelist_preview
        pattern = re.compile(rf"{rtarget}")

        if pmodel:
            for i in range(pmodel.rowCount()):
                preview_basename = os.path.basename(plist[i])
                if not self.MainWindow.cbx_wordwrap.isChecked():
                    if rtarget in preview_basename:
                        # Its preview
                        pmodel.item(i).setText(preview_basename.replace(rtarget, rdest))
                        pmodel.item(i).setForeground(self.brush_preview)
                    else:
                        pmodel.item(i).setForeground(self.brush_unselect)
                else:
                    matches = pattern.finditer(preview_basename)
                    matches_rp = pattern.finditer(preview_basename)
                    if self._lenci(matches) > 0:
                        re_replace = ""
                        for match in matches_rp:
                            fl = preview_basename
                            span = match.span()
                            for j in range(len(fl)):
                                if j == span[1] - 1:
                                    re_replace = re_replace[:span[0]] + str(rdest)
                                else:
                                    re_replace += str(fl[j])
                            break
                        pmodel.item(i).setText(re_replace)
                        pmodel.item(i).setForeground(self.brush_preview)
                    else:
                        pmodel.item(i).setForeground(self.brush_unselect)

    def replace_apply(self):
        # preview model -> apply to flist -> os.rename
        self.replace_changed()
        self.replace_preview()

        pmodel = self.MainWindow.lv_preview.model()
        flist = self.cwd_filelist
        plist = self.cwd_filelist_preview
        str_builder = "Files affected:"
        str_question = "If push OK:"
        samefile = []

        if pmodel:
            for i in range(pmodel.rowCount()):
                fpath = os.path.dirname(plist[i])
                fbase = pmodel.item(i).text()
                obase = os.path.basename(plist[i])

                if fbase != os.path.basename(plist[i]):
                    str_builder = f"{str_builder}\n{obase} -> {fbase}"
                    fapply = os.path.join(fpath, fbase)
                    plist[i] = fapply
        else:
            self.MainWindow.lbl_affected.setText("Nothing happened (No items)")   
            return

        str_explode = str_builder.split("\n")

        if len(str_explode) == 1:
            self.MainWindow.lbl_affected.setText("Nothing happened (No candidates)")   
            return

        for i in range(1, len(str_explode)):
            str_question = f"{str_question}\n{str_explode[i]}"
            if i >= 10:
                str_question = f"{str_question}...\nAnd {len(str_explode) - (i + 1)} more files"
                break

        reply = QMessageBox.question(self.MainWindow, "Confirm", str_question,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            for i in range(len(flist)):
                if flist[i] != plist[i]:
                    try:
                        os.rename(flist[i], plist[i])
                    except FileExistsError:
                        fileexists = os.path.splitext(plist[i])[0] + f"-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}" + os.path.splitext(plist[i])[-1]
                        os.rename(flist[i], 
                                  fileexists)

                        samefile.append(fileexists)
                        
            if len(samefile) > 0:
                str_builder = "\n" + str_builder + "\n\n" + "Conflicted file name has been changed:"
                for i, sfname in enumerate(samefile):
                    str_builder = f"{str_builder}\n{sfname}"

            self.MainWindow.lbl_affected.setText(str_builder)                    
            self.populate_listview(self.cwd)
            self.replace_changed()
            self.MainWindow.tbx_replace_dest.setPlainText("")
        else:
            str_builder = "Change aborted"
            self.MainWindow.lbl_affected.setText(str_builder)                 
            self.populate_listview(self.cwd)   
            self.MainWindow.tbx_replace_dest.setPlainText("")