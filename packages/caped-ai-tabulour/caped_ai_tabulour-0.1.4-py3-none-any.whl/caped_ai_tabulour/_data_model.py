from qtpy import QtCore, QtGui
import pandas as pd
import numpy as np
import math


class pandasModel(QtCore.QAbstractTableModel):
    signalMyDataChanged = QtCore.Signal(object, object, object)

    def __init__(self, data: pd.DataFrame):
        QtCore.QAbstractTableModel.__init__(self)
        self._data = data

    def get_data(self):
        return self._data

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.ToolTipRole:
                return QtGui.QBrush(QtCore.Qt.magenta)
            elif role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
                columnName = self._data.columns[index.column()]
                realRow = index.row()
                retVal = self._data.loc[realRow, columnName]
                if isinstance(retVal, np.float64):
                    retVal = float(retVal)
                elif isinstance(retVal, np.int64):
                    retVal = int(retVal)
                elif isinstance(retVal, np.bool_):
                    retVal = str(retVal)
                elif isinstance(retVal, list):
                    retVal = str(retVal)
                elif isinstance(retVal, str) and retVal == "nan":
                    retVal = ""
                if isinstance(retVal, float) and math.isnan(retVal):
                    retVal = ""
                return retVal
            elif role == QtCore.Qt.FontRole:
                columnName = self._data.columns[index.column()]
                if columnName == "Symbol":
                    font = QtGui.QFont("Arial")
                    font.setPointSize(16)
                    return font
            elif role == QtCore.Qt.ForegroundRole:
                return None  # No specific foreground role
            elif role == QtCore.Qt.BackgroundRole:
                columnName = self._data.columns[index.column()]
                if columnName == "Face Color":
                    realRow = self._data.index[index.row()]
                    face_color = self._data.loc[realRow, "Face Color"]
                    face_color = face_color[0] + face_color[7:9] + face_color[1:7]
                    return QtGui.QColor(face_color)
                elif index.row() % 2 == 0:
                    return QtGui.QColor("#444444")
                else:
                    return QtGui.QColor("#666666")
        return None

    def headerData(self, col, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                try:
                    return self._data.columns[col]
                except IndexError:
                    print(
                        f"IndexError for col:{col} len:{len(self._data.columns)}, shape:{self._data.shape}"
                    )
        elif orientation == QtCore.Qt.Vertical:
            return col
        return None

    def rowCount(self, parent=None):
        if self._data is not None:
            return self._data.shape[0]
        return 0

    def columnCount(self, parent=None):
        if self._data is not None:
            return self._data.shape[1]
        return 0
