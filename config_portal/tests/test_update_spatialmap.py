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


def test_check_catalog_xlsx():
    str1 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")
    b1 = decode_str(str1)
    validate.check_catalog_xlsx(
        b1, FD["volumetric-map"]["downloads"]["depot"], "downloads"
    )
    assert Path(FD["volumetric-map"]["downloads-file"]["depot"]).exists() is True


def test_get_volumetric_map_folder():
    str1 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")
    b1 = decode_str(str1)
    validate.check_catalog_xlsx(b1, "/home/nonroot/app/examples", "downloads")
    assert validate.get_volumetric_map_folder(
        "S1-12proteomics.xlsx", FD["volumetric-map"]["downloads-file"]["depot"]
    ) == (True, "S1-12")


def test_process_volumetric_map_data():
    # expect success
    str1 = make_upload_content("/home/nonroot/app/examples/volumetric-map-data.xlsx")
    b1 = decode_str(str1)
    str2 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")
    b2 = decode_str(str2)
    str3 = make_upload_content(
        f"{FD['volumetric-map']['downloads']['publish']}/S1-12/S1-12proteomics.xlsx"
    )
    b3 = decode_str(str3)

    # expect failure
    str4 = make_upload_content(
        "/home/nonroot/app/tests/test-files/volumetric-map/bad-headers/volumetric-map-data.xlsx"
    )
    b4 = decode_str(str4)
    str5 = make_upload_content(
        "/home/nonroot/app/tests/test-files/volumetric-map/bad-workbook/volumetric-map-data.xlsx"
    )
    b5 = decode_str(str5)
    str6 = make_upload_content(
        "/home/nonroot/app/tests/test-files/downloads/bad-headers/downloads.xlsx"
    )
    b6 = decode_str(str6)
    str7 = make_upload_content("/home/nonroot/app/examples/images-example.xlsx")
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


def test_convert_img_to_greyscale_array():
    width = 500
    height = 100
    p = Path(
        "/home/nonroot/app/tests/test-files/volumetric-map/layers/S1-1-1_C00002.png"
    )
    img_arr = validate.convert_img_to_greyscale_array(p, (width, height))

    assert img_arr.shape == (100, 500)
    assert img_arr.min() == 0
    assert img_arr.max() == 255
    assert img_arr.dtype == "uint8"


def test_process_image_layer_data():
    # expect success
    str1 = make_upload_content("/home/nonroot/app/examples/image-layers-metadata.xlsx")
    b1 = decode_str(str1)
    str2 = make_upload_content(
        "/home/nonroot/app/tests/test-files/volumetric-map/layers/S1-12_L0.png"
    )
    b2 = decode_str(str2)

    # expect failure
    str3 = make_upload_content(
        "/home/nonroot/app/tests/test-files/volumetric-map/layers/S1-1-1_C00002.png"
    )
    b3 = decode_str(str3)
    str4 = make_upload_content("/home/nonroot/app/examples/images-example.xlsx")
    b4 = decode_str(str4)
    str5 = make_upload_content(
        f"{FD['obj-files']['volumes']['publish']}/S1_Sphere_Lower_S1-1.obj"
    )
    b5 = decode_str(str5)

    assert (
        validate.process_image_layer_data(b1, "image-layers-metadata.xlsx")[0] is True
    )
    assert validate.process_image_layer_data(b2, "S1-12_L0.png")[0] is True
    assert validate.process_image_layer_data(b3, "S1-1-1_C00002.png")[0] is False
    assert validate.process_image_layer_data(b4, "images-example.xlsx")[0] is False
    assert validate.process_image_layer_data(b5, "S1_Sphere_Lower_S1-1.obj")[0] is False


def test_upload_image_layers():
    # expect success
    str1 = make_upload_content("/home/nonroot/app/examples/image-layers-metadata.xlsx")
    str2 = make_upload_content(
        "/home/nonroot/app/tests/test-files/volumetric-map/layers/S1-12_L0.png"
    )

    # expect failure
    str3 = make_upload_content("/home/nonroot/app/examples/images-example.xlsx")

    result1 = json.loads(
        json.dumps(
            home.upload_image_layers(
                [str1, str2], ["image-layers-metadata.xlsx", "S1-12_L0.png"]
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result1[0]["props"]["header_class_name"] == "text-success"

    result2 = json.loads(
        json.dumps(
            home.upload_image_layers(
                [str1, str3], ["image-layers-metadata.xlsx", "images-example.xlsx"]
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result2[0]["props"]["header_class_name"] == "text-danger"


def test_upload_volumetric_map():
    # expect success
    str1 = make_upload_content("/home/nonroot/app/examples/volumetric-map-data.xlsx")
    str2 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")

    # expect failure
    str3 = make_upload_content("/home/nonroot/app/examples/images-example.xlsx")

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


def test_publish_image_layer_data():
    str1 = make_upload_content("/home/nonroot/app/examples/image-layers-metadata.xlsx")
    b1 = decode_str(str1)
    str2 = make_upload_content(
        "/home/nonroot/app/tests/test-files/volumetric-map/layers/S1-12_L0.png"
    )
    b2 = decode_str(str2)

    validate.process_image_layer_data(b1, "image-layers-metadata.xlsx")
    validate.process_image_layer_data(b2, "S1-12_L0.png")
    validate.publish_image_layer_data()

    img_dest = f"{FD['image-layer']['publish']}/S1-12/layers"
    img_dest_path = Path(img_dest)
    assert img_dest_path.exists() is True
    img_names = [x.name for x in img_dest_path.iterdir()]
    assert "S1-12_L0.txt" in img_names

    metadata_dest_path = Path(FD["image-layer"]["publish"])
    metadata_names = [y.name for y in metadata_dest_path.iterdir()]
    assert "images.csv" in metadata_names
    assert "colorscales.csv" in metadata_names
