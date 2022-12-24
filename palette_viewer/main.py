import sys
import os
import csv
import re
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QColor
from PyQt6.QtWidgets import QFileDialog, QWidget, QVBoxLayout, QScrollArea


# landmakrj 0, 1, 2, 3
ROMFILES = ["e61-13.20", "e61-12.19", "e61-11.18", "e61-10.17"]

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, name, addr, length, data):
        super(TableModel, self).__init__()
        self._data = _data = {"name": name, "addr": addr, "length": length,
    "data": data}

    def data(self, index, role):
        qcolor = self._data["data"][index.column() + 16*(index.row())]
        if role == Qt.ItemDataRole.DisplayRole:
            c,m,y,k,a = qcolor.getCmyk()
            r,g,b,a = qcolor.getRgb()
            return (f"{c:02x}{m:02x}{y:02x}:{k:02x}") ##{r:02x}{g:02x}{b:02x}\n
        elif role == Qt.ItemDataRole.DecorationRole:
            return QColor(qcolor)

    def rowCount(self, index):
        return self._data["length"] // 16

    def columnCount(self, index):
        return 16 #self._data["length"]

    def clicked(self, i):
        print(i.column())
        #qcolor = self._data["data"][column + 16*row]
        #self._data["data"][column + 16*row] = QColorDialog.getColor(initial = qcolor)

#    def add(self, name, addr, length, data):
#        _data = {"name": name, "addr": addr, "length": length, "data": data}


class MainWindow(QtWidgets.QMainWindow):
    ROMDir = None
    pal_sources = []
    tables = {}
    
    def __init__(self):
        super().__init__()
        openFile = QAction(None, 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.triggered.connect(self.openROM)
        saveTXT = QAction(None, 'Export', self)
        saveTXT.setShortcut('Ctrl+S')
        saveTXT.triggered.connect(self.saveTXT)
        loadTXT = QAction(None, 'Import', self)
        loadTXT.setShortcut('Ctrl+I')
        loadTXT.triggered.connect(self.loadTXT)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.widget = QWidget()
        self.scroll = QScrollArea()
        self.layout = QVBoxLayout(self.widget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        #self.scroll.setVerticalScrollBarPolicy(1)
        self.setCentralWidget(self.scroll)
        self.setGeometry(400, 100, 1000, 1000)

    def saveTXT(self):
        for src in tables:
            
    def openROM(self):
        #home_dir = str(os.path.expanduser("~"))
        home_dir = str(os.path.expanduser("~/yanfen/Downloads/output/mame0239/roms/"))
        self.ROMDir = QFileDialog.getExistingDirectory(self,
                                                       str("Load Unzipped ROM"),
                                                       home_dir)
        self.readPalSources(self.ROMDir)
        self.loadBytes(self.ROMDir)

    def readPalSources(self, dir):
        with open('landmakrj_palette.csv', mode='r') as f:
            csv_record = csv.DictReader(f)
            for row in csv_record:
                if re.match("PALROM_tile", row["Name"]):
                        self.pal_sources.append({"name":row["Name"],
                                                "addr":int(row["Location"],16),
                                                "length":0x10})
                elif re.match("PALROM_building", row["Name"]):
                        self.pal_sources.append({"name":row["Name"],
                                                "addr":int(row["Location"],16),
                                                "length":0x20})

    def loadBytes(self, dir):
        datlist=[open(os.path.join(dir,f),'rb') for f in ROMFILES]
        self.pal_sources.sort(key=lambda p: p["name"])
        for pal in self.pal_sources:
            if pal["addr"] % 4 != 0: raise Exception("first byte not 4-byte align")
            [f.seek(pal["addr"] // 4, 0) for f in datlist]
            colors = []
            for p in range(pal["length"]):
                a,r,g,b = [f.read(1) for f in datlist]
                colors.append(QColor(r[0],g[0],b[0],0xFF - a[0]))

            self.addTable(pal, colors)
        [f.close() for f in datlist]

    def addTable(self, pal, data):
        t = QtWidgets.QTableView()
        t.verticalHeader().setVisible(False)
        t.horizontalHeader().setVisible(False)
        t.setModel(TableModel(pal["name"], pal["addr"],
                              pal["length"], data))
        t.clicked.connect(self.clicked)
        self.layout.addWidget(QtWidgets.QLabel(pal["name"], self))
        self.layout.addWidget(t)
        self.tables[pal["name"]] = t

    def clicked(self, i):
        i.model().clicked(i)
        

app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
sys.exit(app.exec())
