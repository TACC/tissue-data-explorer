import os
import sys
import pandas as pd

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import app
from config_components import validate
from pages import home
from pages.constants import FILE_DESTINATION as FD
from helpers import make_upload_content, decode_str


def dummy_function(file: bytes, which_headers: str) -> tuple[bool, str]:
    """Used in test_process_content"""
    return True, ""


def test_process_si_block_file():
    str1 = make_upload_content("/app/examples/images-example.xlsx")
    b1 = decode_str(str1)
    assert validate.process_si_block_file(b1, "si-block") == (True, "")

    # check that files are in depot
    blocks = pd.read_csv(f"{FD["si-block"]["block-data"]["depot"]}")
    si_files = pd.read_csv(f"{FD["si-block"]["si-files"]["depot"]}")

    # check number of rows and columns in each file
    assert len(blocks.columns) == 8
    assert len(si_files.columns) == 8
    assert blocks.shape[0] == 8
    assert si_files.shape[0] == 6

    # check failure condition
    str2 = make_upload_content("/app/examples/downloads.xlsx")
    b2 = decode_str(str2)

    assert validate.process_si_block_file(b2, "si-block") == (
        False,
        "Worksheet names must match the template.",
    )


def test_check_excel_headers():
    str1 = make_upload_content("/app/examples/images-example.xlsx")
    b1 = decode_str(str1)
    str2 = make_upload_content("/app/examples/downloads.xlsx")
    b2 = decode_str(str2)
    str3 = make_upload_content("/app/examples/volumetric-map-data.xlsx")
    b3 = decode_str(str3)
    str4 = make_upload_content("/app/examples/obj-files.xlsx")
    b4 = decode_str(str4)

    assert validate.check_excel_headers(b1, "si-block")[0] is True
    assert validate.check_excel_headers(b2, "downloads")[0] is True
    assert validate.check_excel_headers(b3, "volumetric-map", fillna=False)[0] is True
    assert validate.check_excel_headers(b4, "obj-files", fillna=False)[0] is True

    assert validate.check_excel_headers(b1, "downloads")[0] is False
    assert validate.check_excel_headers(b2, "volumetric-map")[0] is False
    assert validate.check_excel_headers(b3, "obj-files")[0] is False
    assert validate.check_excel_headers(b4, "si-block")[0] is False


def test_update_links():
    data = {
        "Tissue Block": ["S1-1", "S1-14"],
        "Images": [" ", True],
        "Reports": [True, " "],
        "Volumetric Map": [True, " "],
    }
    df = pd.DataFrame(data=data)
    validate.update_links("Images", df)
    assert df.loc[0, "Images"] == " "
    assert df.loc[1, "Images"] == "/scientific-images-list/S1-14"

    validate.update_links("Reports", df)
    assert df.loc[0, "Reports"] == "/reports"
    assert df.loc[1, "Reports"] == " "

    validate.update_links("Volumetric Map", df)
    assert df.loc[0, "Volumetric Map"] == "volumetric-map/S1-1"
    assert df.loc[1, "Volumetric Map"] == " "


def test_publish_si_block():
    pass


def test_update_si_block_output():
    pass


def test_process_content():
    # make content strings
    str1 = make_upload_content("/app/examples/downloads.xlsx")
    str2 = make_upload_content(
        f"{FD["obj-files"]["volumes"]["publish"]}/S1_Sphere_Lower_S1-1.obj"
    )
    str3 = ""

    assert validate.process_content(
        str1, "downloads.xlsx", "excel", dummy_function
    ) == (True, "")
    assert validate.process_content(
        str2, "S1_Sphere_Lower_S1-1.obj", "excel/vol", dummy_function
    ) == (True, "")
    assert validate.process_content(str3, "", "excel/vol", dummy_function) == (
        False,
        "One or more files were too large.",
    )
    assert validate.process_content(
        str1, "downloads.xlsx", "image", dummy_function
    ) == (False, "Invalid file type xlsx")


def test_check_file_type():
    str1 = make_upload_content("/app/examples/downloads.xlsx")
    str2 = make_upload_content(
        f"{FD["obj-files"]["volumes"]["publish"]}/S1_Sphere_Lower_S1-1.obj"
    )
    str3 = make_upload_content(
        f"{FD["sci-images"]["publish"]}/S1-14/S1-14-1/S1-14-1_C00000.png"
    )
    str4 = make_upload_content(
        f"{FD["sci-images"]["publish"]}/S1-14/S1-14-1/S1-14-1.tif"
    )
    b1 = decode_str(str1)
    b2 = decode_str(str2)
    b3 = decode_str(str3)
    b4 = decode_str(str4)

    # types that should be correct
    assert validate.check_file_type(b1, "excel", "downloads.xlsx") == (True, "")
    assert validate.check_file_type(b1, "excel/vol", "downloads.xlsx") == (True, "")
    assert validate.check_file_type(b1, "3d", "downloads.xlsx") == (True, "")
    assert validate.check_file_type(b2, "excel/vol", "S1_Sphere_Lower_S1-1.obj") == (
        True,
        "",
    )
    assert validate.check_file_type(b2, "3d", "S1_Sphere_Lower_S1-1.obj") == (True, "")
    assert validate.check_file_type(b3, "image", "S1-14-1_C00000.png") == (True, "")
    assert validate.check_file_type(b4, "image", "S1-14-1.tif") == (True, "")

    # types that should not be correct
    assert validate.check_file_type(b4, "excel", "S1-14-1.tif") == (
        False,
        "Invalid file type tif",
    )
    assert validate.check_file_type(b4, "excel/vol", "S1-14-1.tif") == (
        False,
        "Invalid file type tif",
    )
    assert validate.check_file_type(b4, "3d", "S1-14-1.tif") == (
        False,
        "Invalid file type tif",
    )
