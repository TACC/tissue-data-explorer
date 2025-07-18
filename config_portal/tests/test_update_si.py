import os
import sys
import shutil
from pathlib import Path
import pandas as pd
import json
import plotly

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import app
from config_components import validate
from pages import home
from pages.constants import FILE_DESTINATION as FD
from helpers import make_upload_content, decode_str, clean_dir


def test_check_image_name():
    names = {"File": ["S1-1-1.tif", "S1-1-1_C00000.png"]}
    names_df = pd.DataFrame(data=names)

    # expect success
    assert validate.check_image_name("S1-1-1.tif", names_df)[0] == 1
    assert validate.check_image_name("S1-1-1_C00000.png", names_df)[0] == 1

    # expect failure
    assert validate.check_image_name("test.tif", names_df)[0] == 0
    assert validate.check_image_name("S1-1-1.png", names_df)[0] == 0


def test_check_png_name_ending():
    # expect success
    filename1 = "S1-1-1_C00000.png"
    nameparts1 = filename1.split("_C")
    assert validate.check_png_name_ending(filename1, nameparts1)[0] is True

    filename2 = "S1-1-1_C_C00000.png"
    nameparts2 = filename2.split("_C")
    assert validate.check_png_name_ending(filename2, nameparts2)[0] is True

    # expect failure
    filename3 = "S1-1-1.png"
    nameparts3 = filename3.split("_C")
    assert validate.check_png_name_ending(filename3, nameparts3)[0] is False

    filename4 = "S1-1-1_C0000.png"
    nameparts4 = filename4.split("_C")
    assert validate.check_png_name_ending(filename4, nameparts4)[0] is False


def test_process_sci_image():
    str1 = make_upload_content(
        f"{FD["sci-images"]["publish"]}/S1-1/S1-1-1/S1-1-1_C00000.png"
    )
    b1 = decode_str(str1)
    str2 = make_upload_content("/app/examples/images-example.xlsx")
    b2 = decode_str(str2)

    assert validate.process_sci_image(b1, "S1-1-1_C00000.png")[0] is True
    assert validate.process_sci_image(b2, "images-example.xlsx")[0] is False

    # clean up depot directory
    cleanup_status = clean_dir(FD["sci-images"]["depot"])
    assert cleanup_status[0] is True


def test_upload_sci_images():
    str1 = make_upload_content(
        f"{FD["sci-images"]["publish"]}/S1-1/S1-1-1/S1-1-1_C00000.png"
    )
    str2 = make_upload_content("/app/examples/images-example.xlsx")

    # expect success
    result1 = json.loads(
        json.dumps(
            home.upload_sci_images([str1], ["S1-1-1_C00000.png"]),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result1[0]["props"]["header_class_name"] == "text-success"

    # expect failure
    result2 = json.loads(
        json.dumps(
            home.upload_sci_images([str2], ["images-example.xlsx"]),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result2[0]["props"]["header_class_name"] == "text-danger"

    # clean up depot directory
    cleanup_status = clean_dir(FD["sci-images"]["depot"])
    assert cleanup_status[0] is True


def test_move_sci_image():
    # put a file in the depot
    demo_src = Path(f"{FD["sci-images"]["publish"]}/S1-14/S1-14-1/S1-14-1.tif")
    demo_dest = Path(FD["sci-images"]["depot"])
    shutil.move(demo_src, demo_dest)

    # test that the file is moved successfully
    test_src = Path(f"{FD["sci-images"]["depot"]}/S1-14-1.tif")
    test_dest = Path(f"{FD["sci-images"]["publish"]}/S1-14/S1-14-1")
    files = test_dest.iterdir()
    num_files = len([file for file in files if file.is_file()])
    assert num_files == 1

    validate.move_sci_image(test_src, test_dest, "S1-14-1.tif")
    files = test_dest.iterdir()
    num_files = len([file for file in files if file.is_file()])
    assert num_files == 2

    files = [file for file in demo_dest.iterdir() if file.is_file()]
    assert f"{FD["sci-images"]["depot"]}/S1-14-1.tif" not in files
