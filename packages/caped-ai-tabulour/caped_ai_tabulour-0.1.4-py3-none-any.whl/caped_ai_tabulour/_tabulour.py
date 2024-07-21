from typing import List, Union, Dict

import napari
import pandas as pd
from qtpy import QtCore, QtGui, QtWidgets

from ._data_model import pandasModel


class Tabulour(QtWidgets.QTableView):

    signalSelectionChanged = QtCore.Signal(object, object)
    signalDataChanged = QtCore.Signal(str, set, pd.DataFrame)

    def __init__(
        self,
        parent=None,
        viewer: napari.Viewer = None,
        layer: napari.layers.Layer = None,
        data: pd.DataFrame = None,
        zcalibration: int = 1,
        ycalibration: int = 1,
        xcalibration: int = 1,
        time_key: Union[int, str] = None,
        id_key: Union[int, str] = None,
        size_key: Union[int, str] = None,
        dividing_key: Union[int, str] = None,
        fate_key: Union[int, str] = None,
        unique_tracks: dict = None,
        unique_track_properties: dict = None,
        boxes: List = [],
        sizes: List = [],
        plugin=None,
        dividing_choices=None,
        normal_choices=None,
        goblet_choices=None,
        basal_choices=None,
        radial_choices=None,

    ):

        super().__init__(parent)
        self._layer = layer
        self._viewer = viewer
        if data is not None:
            self._data = pandasModel(data)
        else:
            self._data = None
        self._time_key = time_key
        self._id_key = id_key
        self._size_key = size_key
        self._dividing_key = dividing_key
        self._fate_key = fate_key
        self._unique_tracks = unique_tracks
        self._unique_track_properties = unique_track_properties
        self._boxes = boxes
        self._sizes = sizes
        self._zcalibration = zcalibration
        self._ycalibration = ycalibration
        self._xcalibration = xcalibration
        self._plugin = plugin
        self._dividing_choices = dividing_choices
        self._normal_choices = normal_choices
        self._goblet_choices = goblet_choices
        self._basal_choices = basal_choices 
        self._radial_choices = radial_choices

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)

        # allow discontinuous selections (with command key)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setSortingEnabled(True)

        self._set_model()
        self._unique_cell_val = None
        self._unique_cell_val_properties = None
        # to allow click on already selected row
        # self.clicked.connect(self._on_user_click)

    @property
    def viewer(self):
        return self._viewer

    @viewer.setter
    def viewer(self, value):
        self._viewer = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        self._layer = value

    @property
    def time_key(self):
        return self._time_key

    @time_key.setter
    def time_key(self, value):
        self._time_key = value

    @property
    def id_key(self):
        return self._id_key

    @id_key.setter
    def id_key(self, value):
        self._id_key = value

    @property
    def dividing_key(self):
        return self._dividing_key

    @dividing_key.setter
    def dividing_key(self, value):
        self._dividing_key = value

    @property
    def fate_key(self):
        return self._fate_key

    @fate_key.setter
    def fate_key(self, value):
        self._fate_key = value


    @property
    def unique_tracks(self):
        return self._unique_tracks

    @unique_tracks.setter
    def unique_tracks(self, value):
        self._unique_tracks = value

    @property
    def unique_track_properties(self):
        return self._unique_track_properties

    @unique_track_properties.setter
    def unique_track_properties(self, value):
        self._unique_track_properties = value

    @property
    def size_key(self):
        return self._size_key

    @size_key.setter
    def size_key(self, value):
        self._size_key = value

    @property
    def boxes(self):
        return self._boxes

    @boxes.setter
    def boxes(self, value):
        self._boxes = value

    @property
    def sizes(self):
        return self._sizes

    @sizes.setter
    def sizes(self, value):
        self._sizes = value

    @property
    def zcalibration(self):
        return self._zcalibration

    @zcalibration.setter
    def zcalibration(self, value):
        self._zcalibration = value

    @property
    def ycalibration(self):
        return self._ycalibration

    @ycalibration.setter
    def ycalibration(self, value):
        self._ycalibration = value

    @property
    def xcalibration(self):
        return self._xcalibration

    @xcalibration.setter
    def xcalibration(self, value):
        self._xcalibration = value

    @property
    def plugin(self):
        return self._plugin

    @plugin.setter
    def plugin(self, value):
        self._plugin = value

    @property
    def dividing_choices(self):
        return self._dividing_choices

    @dividing_choices.setter
    def dividing_choices(self, value):
        self._dividing_choices = value

    @property
    def goblet_choices(self):
        return self._goblet_choices

    @goblet_choices.setter
    def goblet_choices(self, value):
        self._goblet_choices = value    

    @property
    def basal_choices(self):
        return self._basal_choices

    @basal_choices.setter
    def basal_choices(self, value):
        self._basal_choices = value

    @property
    def radial_choices(self):
        return self._radial_choices

    @radial_choices.setter
    def radial_choices(self, value):
        self._radial_choices = value

    @property
    def normal_choices(self):
        return self._normal_choices

    @normal_choices.setter
    def normal_choices(self, value):
        self._normal_choices = value

    def _set_model(self):

        if self._data is not None:
            self.proxy = QtCore.QSortFilterProxyModel()
            self.proxy.setSourceModel(self._data)
            self.setModel(self.proxy)
            self._refreshColumns()

    def _refreshColumns(self):

        columns = self._data.get_data().columns
        for column in columns:
            colIdx = columns.get_loc(column)
            self.setColumnHidden(colIdx, False)

    def contextMenuEvent(self, event):
        self.menu = QtWidgets.QMenu(self)
        saveAction = QtWidgets.QAction("Save", self)
        saveAction.triggered.connect(lambda: self.save(event))
        self.menu.addAction(saveAction)
        self.menu.popup(QtGui.QCursor.pos())

    def save(self, event):

        name = QtWidgets.QFileDialog.getSaveFileName(self, "Save File")[0]
        self._data.get_data().to_csv(name + ".csv", index=False)

    def _on_user_click(self, item):

        row = self.proxy.mapToSource(item).row()
        # column = self.proxy.mapToSource(item).column()
        if (
            self._time_key is not None
            and self._time_key in self._data.get_data()
        ):

            self._viewer.dims.set_point(
                0, int(float(self._data.get_data()[self._time_key][row]))
            )
            self.setStyleSheet(
                """
                QTableView::item:selected:active {
                        background: #013220;
                    }
                """
            )
            # For TrackMate
            if (
                self._id_key is not None
                and self._id_key in self._data.get_data()
            ):

                value_of_interest = int(
                    self._data.get_data()[self._id_key][row]
                )
                if self._unique_tracks is not None:
                    (
                        self._unique_cell_val,
                        self._unique_cell_val_properties,
                    ) = self._display_unique_tracks(
                        value_of_interest=value_of_interest
                    )

                if self._plugin.track_id_box is not None:

                    dividing_normal = eval(
                        self._data.get_data()[self._dividing_key][row]
                    )
                    fate = eval(
                        self._data.get_data()[self._fate_key][row]
                    )
                  


                    if dividing_normal:
                        self.plugin.track_model_type.value = "Mitosis"
                        self.plugin.track_id_box.choices = (
                            self._dividing_choices
                        )
                   


                    else:
                        self.plugin.track_model_type.value = "Non-Mitosis"
                        self.plugin.track_id_box.choices = self._normal_choices

                    self.plugin.track_id_box.value = value_of_interest

    def _display_unique_tracks(self, value_of_interest):

        # Gives back tracklets over time ID, T, Z, Y, X
        if int(value_of_interest) in self._unique_tracks:
            return (
                self._unique_tracks[int(value_of_interest)],
                self._unique_track_properties[int(value_of_interest)],
            )
