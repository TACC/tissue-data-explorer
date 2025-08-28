import os
import sys
import pandas as pd
import json
import plotly
import shutil
from pathlib import Path

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import app
from config_components import validate
from pages import home
from pages.constants import FILE_DESTINATION as FD
from helpers import make_upload_content, decode_str


def test_is_valid_filename():
    assert validate.is_valid_filename(fn="*.xlsx")[0] is False
    assert validate.is_valid_filename(fn="../../run_script.py")[0] is False
    assert validate.is_valid_filename(fn="~/test.sh")[0] is False
    assert validate.is_valid_filename(fn="1 2 3.txt")[0] is True
    assert validate.is_valid_filename(fn="1_2_3.tif")[0] is True
    assert validate.is_valid_filename(fn="a-b-c.jpeg")[0] is True
    assert validate.is_valid_filename(fn="a-b-c.ome.tiff")[0] is True


def test_validate_filename_col():
    df1 = pd.DataFrame(data={"File": ["*.xlsx", "1 2 3.txt"]})
    df2 = pd.DataFrame(data={"File": ["../../run_script.py", "~/test.sh"]})
    df3 = pd.DataFrame(data={"File": ["a-b-c.ome.tiff", "1 2 3.txt"]})

    assert validate.validate_filename_col(df1["File"])[0] is False
    assert validate.validate_filename_col(df2["File"])[0] is False
    assert validate.validate_filename_col(df3["File"])[0] is True


def test_save_generic_file():
    str1 = make_upload_content(FD["si-block"]["block-data"]["publish"])
    b1 = decode_str(str1)

    assert Path("/home/nonroot/app/depot/generic").exists() is False
    validate.save_generic_file("/home/nonroot/app/depot/generic", b1, "blocks.csv")
    assert Path("/home/nonroot/app/depot/generic/blocks.csv").exists() is True
    shutil.rmtree(Path("/home/nonroot/app/depot/generic"))


def test_update_df_entries():
    new_entries = pd.DataFrame(
        data={"File": ["a-b-c-d.obj", "1 2 3.obj"], "Name": ["S1-6", "S1-7"]}
    )

    new_entries_overlap = pd.DataFrame(
        data={"File": ["1_2_3.obj", "1 2 3.obj"], "Name": ["S1-6", "S1-7"]}
    )

    old_entries = pd.DataFrame(
        data={"File": ["1_2_3.obj", "a-b-c.obj"], "Name": ["S1-1", "S1-4"]}
    )

    # test that additions work with no overlap
    updated_df1 = validate.update_df_entries(old_entries, new_entries, "File")
    expected_df1 = pd.DataFrame(
        data={
            "File": ["1_2_3.obj", "a-b-c.obj", "a-b-c-d.obj", "1 2 3.obj"],
            "Name": ["S1-1", "S1-4", "S1-6", "S1-7"],
        }
    )
    assert updated_df1.equals(expected_df1)

    # test that additions work with overlap
    updated_df2 = validate.update_df_entries(old_entries, new_entries_overlap, "File")
    expected_df2 = pd.DataFrame(
        data={
            "File": ["a-b-c.obj", "1_2_3.obj", "1 2 3.obj"],
            "Name": ["S1-4", "S1-6", "S1-7"],
        }
    )
    assert updated_df2.equals(expected_df2)


def test_update_entries():
    blank_loc_str = "./depot/blank/obj-files.csv"
    blank_loc = Path(blank_loc_str)
    if not Path.exists(blank_loc.parent):
        Path.mkdir(blank_loc.parent, parents=True)

    full_loc_str = "/home/nonroot/app/depot/full/obj-files.csv"
    full_loc = Path(full_loc_str)
    if not Path.exists(full_loc.parent):
        Path.mkdir(full_loc.parent, parents=True)

    # copy a test file into full loc
    src = Path("/home/nonroot/app/tests/test-files/obj/obj-files.csv")
    shutil.copyfile(src, full_loc)

    new_df = pd.DataFrame(
        data={
            "Organ": ["C1"],
            "Name": ["Body"],
            "File": ["cube.obj"],
            "Color": ["FF0000"],
            "Opacity": [1],
        }
    )

    # test blank location
    blank_df = validate.update_entries(blank_loc_str, new_df, "File")
    assert blank_df.empty is False
    assert blank_df.shape[0] == 1

    # test non-blank location
    full_df = validate.update_entries(full_loc_str, new_df, "File")
    assert full_df.empty is False
    assert full_df.shape[0] == 10

    # test bad filename
    bad_fn_df = pd.DataFrame(
        data={
            "Organ": ["C1"],
            "Name": ["Body"],
            "File": ["*.obj"],
            "Color": ["FF0000"],
            "Opacity": [1],
        }
    )
    fail_df = validate.update_entries(full_loc_str, bad_fn_df, "File")
    assert fail_df[0] is False

    shutil.rmtree(blank_loc.parent)
    shutil.rmtree(full_loc.parent)


def test_process_obj_files():
    str1 = make_upload_content(
        "/home/nonroot/app/tests/test-files/obj/obj-files-bad-fn/obj-files.xlsx"
    )
    b1 = decode_str(str1)
    str2 = make_upload_content(
        "/home/nonroot/app/tests/test-files/obj/obj-files-bad-headers/obj-files.xlsx"
    )
    b2 = decode_str(str2)
    str3 = make_upload_content("/home/nonroot/app/examples/obj-files.xlsx")
    b3 = decode_str(str3)
    str4 = make_upload_content(
        f"{FD["obj-files"]["volumes"]["publish"]}/S1_Sphere_Lower_S1-1.obj"
    )
    b4 = decode_str(str4)

    assert validate.process_obj_files(b1, "obj-files.xlsx")[0] is False
    assert validate.process_obj_files(b2, "obj-files.xlsx")[0] is False
    assert validate.process_obj_files(b3, "obj-files.xlsx")[0] is True
    assert validate.process_obj_files(b4, "S1_Sphere_Lower_S1-1.obj")[0] is True


def test_update_obj_files_output():
    # will cause failure
    str1 = make_upload_content(
        "/home/nonroot/app/tests/test-files/obj/obj-files-bad-headers/obj-files.xlsx"
    )
    # should succeed
    str2 = make_upload_content("/home/nonroot/app/examples/obj-files.xlsx")
    str3 = make_upload_content(
        f"{FD["obj-files"]["volumes"]["publish"]}/S1_Sphere_Lower_S1-1.obj"
    )

    result1 = json.loads(
        json.dumps(
            home.update_obj_files_output(
                [str2, str3], ["obj-files.xlsx", "S1_Sphere_Lower_S1-1.obj"]
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result1[0]["props"]["header_class_name"] == "text-success"

    result2 = json.loads(
        json.dumps(
            home.update_obj_files_output(
                [str1, str3], ["obj-files.xlsx", "S1_Sphere_Lower_S1-1.obj"]
            ),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result2[0]["props"]["header_class_name"] == "text-danger"


def test_publish_obj_files():
    # depends on successful completion of test_update_obj_files_output
    validate.publish_obj_files()
    assert (
        Path(f"{FD["obj-files"]["summary"]["publish"]}/obj-files.csv").exists() is True
    )
    assert (
        Path(
            f"{FD["obj-files"]["volumes"]["publish"]}/S1_Sphere_Lower_S1-1.obj"
        ).exists()
        is True
    )
