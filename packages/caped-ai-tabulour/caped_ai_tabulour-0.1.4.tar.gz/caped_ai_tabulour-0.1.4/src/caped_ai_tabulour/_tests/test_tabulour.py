import napari
import pandas as pd

from caped_ai_tabulour._tabulour import Tabulour


def test_table():

    d = {
        "time": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
        ],
        "value": [
            3,
            4,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
        ],
        "brinjal": [
            10,
            20,
            30,
            40,
            50,
            60,
            70,
            80,
            90,
            100,
            111,
            121,
            131,
            141,
            151,
            161,
            171,
            181,
            191,
            201,
        ],
        "tomato": [
            3,
            4,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
        ],
    }
    data = pd.DataFrame(data=d, columns=["time", "value", "brinjal", "tomato"])
    viewer = napari.Viewer()
    unique_cells = {}
    unique_cells[121] = {"Name": 1, "Age": 12}
    table_tab = Tabulour(
        viewer=viewer,
        data=data,
        time_key="time",
        other_key="brinjal",
        unique_cells=unique_cells,
    )

    viewer.window.add_dock_widget(table_tab)
    napari.run()


if __name__ == "__main__":
    test_table()
