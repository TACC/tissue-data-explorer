import os
import sys
import pandas as pd
from pathlib import Path
import shutil
import plotly
import json

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import app
from config_components import validate
from pages import home
from pages.constants import FILE_DESTINATION as FD
from helpers import make_upload_content, decode_str, clean_dir


def dummy_function(file: bytes, which_headers: str) -> tuple[bool, str]:
    """Used in test_process_content"""
    return True, ""


def test_process_si_block_file():
    str1 = make_upload_content("/home/nonroot/app/examples/images-example.xlsx")
    b1 = decode_str(str1)
    assert validate.process_si_block_file(b1, "si-block") == (True, "")

    # check that files are in depot
    blocks = pd.read_csv(f"{FD['si-block']['block-data']['depot']}")
    si_files = pd.read_csv(f"{FD['si-block']['si-files']['depot']}")

    # check number of rows and columns in each file
    assert len(blocks.columns) == 8
    assert len(si_files.columns) == 8
    assert blocks.shape[0] == 8
    assert si_files.shape[0] == 6

    # check failure condition
    str2 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")
    b2 = decode_str(str2)

    assert validate.process_si_block_file(b2, "si-block") == (
        False,
        "Worksheet names must match the template.",
    )

    # clean up depot directory
    cleanup_status = clean_dir(FD["si-block"]["block-data"]["depot"])
    assert cleanup_status[0] is True


def test_check_excel_headers():
    str1 = make_upload_content("/home/nonroot/app/examples/images-example.xlsx")
    b1 = decode_str(str1)
    str2 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")
    b2 = decode_str(str2)
    str3 = make_upload_content("/home/nonroot/app/examples/volumetric-map-data.xlsx")
    b3 = decode_str(str3)
    str4 = make_upload_content("/home/nonroot/app/examples/obj-files.xlsx")
    b4 = decode_str(str4)

    assert validate.check_excel_headers(b1, "si-block")[0] is True
    assert validate.check_excel_headers(b2, "downloads")[0] is True
    assert validate.check_excel_headers(b3, "volumetric-map")[0] is True
    assert validate.check_excel_headers(b4, "obj-files")[0] is True

    assert validate.check_excel_headers(b1, "downloads")[0] is False
    assert validate.check_excel_headers(b2, "volumetric-map")[0] is False
    assert validate.check_excel_headers(b3, "obj-files")[0] is False
    assert validate.check_excel_headers(b4, "si-block")[0] is False


def test_update_links():
    data = {
        "Tissue Block": ["S1-1", "S1-14"],
        "Images": [None, True],
        "Reports": [True, None],
        "Volumetric Map": [True, None],
    }
    df = pd.DataFrame(data=data)
    validate.update_links("Images", df)
    assert df.loc[0, "Images"] is None
    assert df.loc[1, "Images"] == "/scientific-images-list/S1-14"

    validate.update_links("Reports", df)
    assert df.loc[0, "Reports"] == "/reports"
    assert df.loc[1, "Reports"] is None

    validate.update_links("Volumetric Map", df)
    assert df.loc[0, "Volumetric Map"] == "/volumetric-map/S1-1"
    assert df.loc[1, "Volumetric Map"] is None


def test_publish_si_block():
    # pd.set_option("display.max_columns", None)
    # pd.set_option("display.max_rows", None)
    # pd.set_option("display.max_colwidth", None)
    # pd.set_option("display.width", None)

    # get original thumbnails and blocks data so it can be reset after tests have run
    tn_df_original = pd.read_csv(FD["thumbnails"]["catalog"])
    block_data_original = pd.read_csv(FD["si-block"]["block-data"]["publish"])
    si_files_original = pd.read_csv(FD["si-block"]["si-files"]["publish"])

    # test the case where nothing has changed in si files or block data
    block_data_original.to_csv(FD["si-block"]["block-data"]["depot"], index=False)
    si_files_original.to_csv(FD["si-block"]["si-files"]["depot"], index=False)

    validate.publish_si_block()

    # test that depot folder is empty
    assert Path(FD["si-block"]["block-data"]["depot"]).exists() is False
    assert Path(FD["si-block"]["si-files"]["depot"]).exists() is False

    # test that publish folder has si files
    assert Path(FD["si-block"]["block-data"]["publish"]).exists() is True
    assert Path(FD["si-block"]["si-files"]["publish"]).exists() is True

    # test that published files have same content since depot files were identical
    tn_df_1 = pd.read_csv(FD["thumbnails"]["catalog"])
    block_data_1 = pd.read_csv(FD["si-block"]["block-data"]["publish"])
    si_file_1 = pd.read_csv(FD["si-block"]["si-files"]["publish"])

    assert block_data_1.equals(block_data_original)
    assert si_file_1.equals(si_files_original)
    assert tn_df_1["Name"].isin(tn_df_original["Name"]).all()

    # test the case where a new image is added
    df1 = pd.DataFrame(
        data={
            "Tissue Block": ["S1-15"],
            "Image Set": ["S1-15-2"],
            "Image Category": ["Optical Clearing"],
            "File": ["S1-15-1.tif"],
            "Height": [600],
            "Width": [600],
            "Slices": [1],
            "Channels": [1],
        }
    )
    df1.to_csv(FD["si-block"]["si-files"]["depot"], index=False)

    validate.publish_si_block()

    si_file_2 = pd.read_csv(FD["si-block"]["si-files"]["publish"])
    tn_df_2 = pd.read_csv(FD["thumbnails"]["catalog"])
    assert si_file_2["File"].str.fullmatch("S1-15-1.tif").any()
    assert tn_df_2["Name"].str.fullmatch("S1-15-1.tif").any()

    # test the case where an image is updated
    df2 = pd.DataFrame(
        data={
            "Tissue Block": ["S1-15"],
            "Image Set": ["S1-15-2"],
            "Image Category": ["Optical Clearing"],
            "File": ["S1-15-2.tif"],
            "Height": [600],
            "Width": [600],
            "Slices": [1],
            "Channels": [1],
        }
    )
    df2.to_csv(FD["si-block"]["si-files"]["depot"], index=False)

    validate.publish_si_block()

    si_file_3 = pd.read_csv(FD["si-block"]["si-files"]["publish"])
    tn_df_3 = pd.read_csv(FD["thumbnails"]["catalog"])
    assert si_file_3["File"].str.fullmatch("S1-15-2.tif").any()
    assert not si_file_3["File"].str.fullmatch("S1-15-1.tif").any()
    assert tn_df_3["Name"].str.fullmatch("S1-15-2.tif").any()
    assert not tn_df_3["Name"].str.fullmatch("S1-15-1.tif").any()

    # clean up files that have been changed by tests
    tn_df_original.to_csv(FD["thumbnails"]["catalog"], index=False)
    block_data_original.to_csv(FD["si-block"]["block-data"]["publish"], index=False)
    si_files_original.to_csv(FD["si-block"]["si-files"]["publish"], index=False)


def test_update_si_block_output():
    str1 = make_upload_content("/home/nonroot/app/examples/images-example.xlsx")
    str2 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")

    # expect success
    result1 = json.loads(
        json.dumps(
            home.update_si_block_output(str1, "images-example.xlsx"),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result1[0]["props"]["header_class_name"] == "text-success"

    # expect failure
    result2 = json.loads(
        json.dumps(
            home.update_si_block_output(str2, "downloads.xlsx"),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result2[0]["props"]["header_class_name"] == "text-danger"

    # clean up depot directory
    cleanup_status = clean_dir(FD["si-block"]["block-data"]["depot"])
    assert cleanup_status[0] is True


def test_process_content():
    # make content strings
    str1 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")
    str2 = make_upload_content(
        f"{FD['obj-files']['volumes']['publish']}/S1_Sphere_Lower_S1-1.obj"
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
    str1 = make_upload_content("/home/nonroot/app/examples/downloads.xlsx")
    str2 = make_upload_content(
        f"{FD['obj-files']['volumes']['publish']}/S1_Sphere_Lower_S1-1.obj"
    )
    str3 = make_upload_content(
        f"{FD['sci-images']['publish']}/S1-14/S1-14-1/S1-14-1_C00000.png"
    )
    str4 = make_upload_content(
        f"{FD['sci-images']['publish']}/S1-14/S1-14-1/S1-14-1.tif"
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


def test_update_thumbnails_record():
    # new_tr: {"Block": [], "Preview": [], "Name": [], "Link": []}
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.width", None)

    # get initial value for thumbnails df
    tn_initial = pd.read_csv(FD["thumbnails"]["catalog"])

    # test adding an entry
    df2 = pd.DataFrame(
        data={
            "Block": ["S1-1"],
            "Preview": [
                "../../assets/config/scientific-images/thumbnails/S1-1-1/S1-1-1_thumbnail.png"
            ],
            "Name": ["S1-1-1.tif"],
            "Link": ["/scientific-images/S1-1/S1-1-1"],
        }
    )
    # del2 = []
    validate.update_thumbnails_record(df2)
    result = pd.read_csv(FD["thumbnails"]["catalog"])
    assert "/scientific-images/S1-1/S1-1-1" in result["Link"].values
    assert len(result["Link"].values) == 6

    # test updating an entry
    df3 = pd.DataFrame(
        data={
            "Block": ["S1-1"],
            "Preview": [
                "../../assets/config/scientific-images/thumbnails/S1-1-1/S1-1-2_thumbnail.png"
            ],
            "Name": ["S1-1-2.tif"],
            "Link": ["/scientific-images/S1-1/S1-1-1"],
        }
    )
    # del3 = []
    validate.update_thumbnails_record(df3)
    result = pd.read_csv(FD["thumbnails"]["catalog"])
    assert len(result["Link"].values) == 6
    assert (
        "../../assets/config/scientific-images/thumbnails/S1-1-1/S1-1-2_thumbnail.png"
        in result["Preview"].values
    )
    assert (
        "../../assets/config/scientific-images/thumbnails/S1-1-1/S1-1-1_thumbnail.png"
        not in result["Preview"].values
    )

    # reset thumbnails df
    tn_initial.to_csv(FD["thumbnails"]["catalog"], index=False)


def test_generate_thumbnail():
    # test removal of old path when new image has not been uploaded yet
    img_set = "TEST-1-1"
    block = "TEST-1"
    namestem = "TEST-IMG-1-1"
    dest = f"{FD['sci-images']['publish']}/{block}/{namestem}"
    thumbnail_loc = f"{FD['thumbnails']['publish']}/{img_set}/{namestem}_thumbnail.png"
    thumbnail_folder = Path(f"{FD['thumbnails']['publish']}/{img_set}")

    if not Path.exists(thumbnail_folder):
        Path.mkdir(thumbnail_folder, parents=True)

    validate.generate_thumbnail(dest, img_set, thumbnail_loc)
    path_status = Path.exists(thumbnail_folder)
    assert path_status is False

    # test scenario where thumbnail is made- images exist to use for thumbnail
    img_set = "S1-1-1"
    block = "S1-1"
    namestem = "S1-1-1"
    dest = f"{FD['sci-images']['publish']}/{block}/{namestem}"
    thumbnail_loc = f"{FD['thumbnails']['publish']}/{img_set}/{namestem}_thumbnail.png"
    thumbnail_folder = Path(f"{FD['thumbnails']['publish']}/{img_set}")
    validate.generate_thumbnail(dest, img_set, thumbnail_loc)
    path_status = Path.exists(thumbnail_folder)
    assert path_status is True
    files = thumbnail_folder.iterdir()
    num_files = len([file for file in files if file.is_file()])
    assert num_files > 0

    # clean up the thumbnail generated by the test
    shutil.rmtree(thumbnail_folder)


def test_get_image_info():
    # name validation is already tested in tests for check_image_name
    # test that match is returned for exact file
    df = pd.read_csv(FD["si-block"]["si-files"]["publish"])
    result = validate.get_image_info("S1-1-1.tif", df)
    assert result[0] is True
    assert result[1] == "S1-1-1"
    assert type(result[2]) is pd.DataFrame
    assert result[2].shape == (1, 8)
    assert result[3] == ""

    # test that match is returned for name stem
    result = validate.get_image_info("S1-1-1_C00000.png", df)
    assert result[0] is True
    assert result[1] == "S1-1-1"
    assert type(result[2]) is pd.DataFrame
    assert result[2].shape == (1, 8)
    assert result[3] == ""


def test_query_thumbnails_for_changed_filenames():
    tn_df_original = pd.read_csv(FD["thumbnails"]["catalog"])
    # test adding new image set
    df1 = pd.DataFrame(
        data={
            "Tissue Block": ["S1-15"],
            "Image Set": ["S1-15-2"],
            "Image Category": ["Optical Clearing"],
            "File": ["S1-15-1.tif"],
            "Height": [600],
            "Width": [600],
            "Slices": [1],
            "Channels": [1],
        }
    )
    result1 = pd.Series(data=["S1-15-1.tif"])
    assert validate.query_thumbnails_for_changed_filenames(df1, tn_df_original).equals(
        result1
    )

    # test changing image mappings
    tn_df = pd.read_csv(FD["thumbnails"]["catalog"])
    df2 = pd.DataFrame(
        data={
            "Tissue Block": ["S1-15"],
            "Image Set": ["S1-15-2"],
            "Image Category": ["Optical Clearing"],
            "File": ["S1-15-2.tif"],
            "Height": [600],
            "Width": [600],
            "Slices": [1],
            "Channels": [1],
        }
    )
    result2 = pd.Series(data=["S1-15-2.tif"])
    assert validate.query_thumbnails_for_changed_filenames(df2, tn_df).equals(result2)

    # test doing both
    tn_df = pd.read_csv(FD["thumbnails"]["catalog"])
    df3 = pd.DataFrame(
        data={
            "Tissue Block": ["S1-15", "S1-15"],
            "Image Set": ["S1-15-2", "S1-15-4"],
            "Image Category": ["Optical Clearing", "Optical Clearing"],
            "File": ["S1-15-1.tif", "S1-15-2.tif"],
            "Height": [600, 600],
            "Width": [600, 600],
            "Slices": [1, 1],
            "Channels": [1, 1],
        }
    )
    result3 = pd.Series(data=["S1-15-1.tif", "S1-15-2.tif"])
    assert validate.query_thumbnails_for_changed_filenames(df3, tn_df).equals(result3)

    # reset thumbnails to original set
    tn_df_original.to_csv(FD["thumbnails"]["catalog"], index=False)
