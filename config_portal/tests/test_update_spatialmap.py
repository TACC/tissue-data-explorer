import os
import sys
import pandas as pd
import json
import plotly
from pathlib import Path

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import app
from config_components import validate
from pages import home
from pages.constants import FILE_DESTINATION as FD
from helpers import make_upload_content, decode_str


def test_make_cubes_df():
    vol_measurements = pd.DataFrame(
        data={
            "X Min": [0],
            "X Max": [4],
            "X Size": [2],
            "Y Min": [0],
            "Y Max": [4],
            "Y Size": [2],
            "Z Min": [0],
            "Z Max": [4],
            "Z Size": [2],
        }
    )
    points_df = pd.DataFrame(
        data={
            "Block ID": [1, 2],
            "X Center": [1.0, 3],
            "Y Center": [1.0, 3],
            "Z Center": [1.0, 3],
            "X Size": [2, 2],
            "Y Size": [2, 2],
            "Z Size": [2, 2],
            "Category": [True, False],
            "CYB5A": [-2, 2],
        }
    )
    expected_cube_df = pd.DataFrame(
        data={
            "Block ID": [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
            "X Center": [
                0.0,
                1.999,
                0.0,
                1.999,
                0.0,
                1.999,
                0.0,
                1.999,
                2.0,
                3.999,
                2.0,
                3.999,
                2.0,
                3.999,
                2.0,
                3.999,
            ],
            "Y Center": [
                0.0,
                0.0,
                1.999,
                1.999,
                0.0,
                0.0,
                1.999,
                1.999,
                2.0,
                2.0,
                3.999,
                3.999,
                2.0,
                2.0,
                3.999,
                3.999,
            ],
            "Z Center": [
                0.0,
                0.0,
                0.0,
                0.0,
                1.999,
                1.999,
                1.999,
                1.999,
                2.0,
                2.0,
                2.0,
                2.0,
                3.999,
                3.999,
                3.999,
                3.999,
            ],
            "X Size": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            "Y Size": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            "Z Size": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            "Category": [
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "CYB5A": [-2, -2, -2, -2, -2, -2, -2, -2, 2, 2, 2, 2, 2, 2, 2, 2],
        },
    )
    cubes_df = validate.make_cubes_df(points_df, vol_measurements)
    pd.testing.assert_frame_equal(cubes_df, expected_cube_df, check_dtype=True)


def test_check_downloads_xlsx():
    str1 = make_upload_content("/app/examples/downloads.xlsx")
    b1 = decode_str(str1)
    validate.check_downloads_xlsx(b1, "downloads.xlsx")
    assert Path(FD["volumetric-map"]["downloads-file"]["depot"]).exists() is True


def test_get_volumetric_map_folder():
    str1 = make_upload_content("/app/examples/downloads.xlsx")
    b1 = decode_str(str1)
    validate.check_downloads_xlsx(b1, "/app/examples/downloads.xlsx")
    assert validate.get_volumetric_map_folder("S1-12proteomics.xlsx") == (True, "S1-12")


def test_process_volumetric_map_data():
    # expect success
    str1 = make_upload_content("/app/examples/volumetric-map-data.xlsx")
    b1 = decode_str(str1)
    str2 = make_upload_content("/app/examples/downloads.xlsx")
    b2 = decode_str(str2)
    str3 = make_upload_content(
        f"{FD['volumetric-map']['downloads']['publish']}/S1-12/S1-12proteomics.xlsx"
    )
    b3 = decode_str(str3)

    # expect failure
    str4 = make_upload_content(
        "/app/tests/test-files/volumetric-map/bad-headers/volumetric-map-data.xlsx"
    )
    b4 = decode_str(str4)
    str5 = make_upload_content(
        "/app/tests/test-files/volumetric-map/bad-workbook/volumetric-map-data.xlsx"
    )
    b5 = decode_str(str5)
    str6 = make_upload_content(
        "/app/tests/test-files/downloads/bad-headers/downloads.xlsx"
    )
    b6 = decode_str(str6)
    str7 = make_upload_content("/app/examples/images-example.xlsx")
    b7 = decode_str(str7)
    str8 = make_upload_content(
        f"{FD['obj-files']['volumes']['publish']}/S1_Sphere_Lower_S1-1.obj"
    )
    b8 = decode_str(str8)

    assert (
        validate.process_volumetric_map_data(b1, "volumetric-map-data.xlsx")[0] is True
    )
    assert validate.process_volumetric_map_data(b2, "downloads.xlsx")[0] is True
    assert validate.process_volumetric_map_data(b3, "S1-12proteomics.xlsx")[0] is True

    assert (
        validate.process_volumetric_map_data(b4, "volumetric-map-data.xlsx")[0] is False
    )
    assert (
        validate.process_volumetric_map_data(b5, "volumetric-map-data.xlsx")[0] is False
    )
    assert validate.process_volumetric_map_data(b6, "downloads.xlsx")[0] is False
    assert validate.process_volumetric_map_data(b7, "images-example.xlsx")[0] is False
    assert validate.process_volumetric_map_data(b8, "images-example.xlsx")[0] is False


def test_upload_volumetric_map():
    # expect success
    str1 = make_upload_content("/app/examples/volumetric-map-data.xlsx")
    str2 = make_upload_content("/app/examples/downloads.xlsx")

    # expect failure
    str3 = make_upload_content("/app/examples/images-example.xlsx")

    result1 = json.loads(
        json.dumps(
            home.upload_volumetric_map(
                [str1, str2], ["volumetric-map-data.xlsx", "downloads.xlsx"]
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result1[0]["props"]["header_class_name"] == "text-success"

    result2 = json.loads(
        json.dumps(
            home.upload_volumetric_map(
                [str1, str3], ["volumetric-map-data.xlsx", "images-example.xlsx"]
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result2[0]["props"]["header_class_name"] == "text-danger"


def test_publish_volumetric_map_data():
    # list all the files in depot
    p = Path(FD["volumetric-map"]["downloads"]["depot"])
    dirs_to_check = [x for x in p.iterdir() if x.is_dir()]

    for dir in dirs_to_check:
        assert dir.exists() is True

    assert Path(FD["volumetric-map"]["downloads-file"]["depot"]).exists() is True

    validate.publish_volumetric_map_data()

    # check that all of the files have been moved to publish
    assert Path(FD["volumetric-map"]["downloads-file"]["publish"]).exists() is True

    for dir in dirs_to_check:
        assert (
            Path(f"{FD['volumetric-map']['downloads']['publish']}/{dir.name}").exists()
            is True
        )
