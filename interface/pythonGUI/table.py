# -*- coding: utf-8 -*-
"""
Created on Tue May  2 20:46:18 2023

@author: Santosh Bag
"""
import sys,os
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView
import tradingDB as tdb


pos_cols = ['Scrip','Instrument','LongShort','Quantity','Orig Liability','Curr Liability','Delta','Theta','PnL']
class TableWidget(QTableWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setRowCount(len(data))
        self.setColumnCount(len(data[0]))
        self.setHorizontalHeaderLabels(pos_cols)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fill_table()

    def fill_table(self):
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(str(cell))
                self.setItem(i, j, item)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     data = tdb.showDB()[1]
#     table = TableWidget(list(data.values))
#     table.show()
#     sys.exit(app.exec_())
