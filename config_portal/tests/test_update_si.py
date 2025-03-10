import os
import sys
import pandas as pd
import json
import plotly

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import app
from config_components import validate
from pages import home
from pages.constants import FILE_DESTINATION as FD
from helpers import make_upload_content, decode_str


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
    assert validate.check_png_name_ending("S1-1-1_C00000.png")[0] is True
    assert validate.check_png_name_ending("S1-1-1_C_C00000.png")[0] is True

    # expect failure
    assert validate.check_png_name_ending("S1-1-1.png")[0] is False
    assert validate.check_png_name_ending("S1-1-1_C0000.png")[0] is False


def test_process_sci_image():
    str1 = make_upload_content(
        f"{FD["sci-images"]["publish"]}/S1-1/S1-1-1/S1-1-1_C00000.png"
    )
    b1 = decode_str(str1)
    str2 = make_upload_content("/app/examples/images-example.xlsx")
    b2 = decode_str(str2)

    assert validate.process_sci_image(b1, "S1-1-1_C00000.png")[0] is True
    assert validate.process_sci_image(b2, "images-example.xlsx")[0] is False


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
