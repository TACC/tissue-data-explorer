import os
import sys
import plotly
import json

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import app
from pages import home
from helpers import make_upload_content


def test_update_reports_output():
    str1 = make_upload_content("/app/examples/reports.xlsx")
    str2 = make_upload_content("/app/examples/images-example.xlsx")

    # expect success
    result1 = json.loads(
        json.dumps(
            home.update_reports_output(str1, "reports.xlsx"),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result1[0]["props"]["header_class_name"] == "text-success"

    # expect failure
    result2 = json.loads(
        json.dumps(
            home.update_reports_output(str2, "images-example.xlsx"),
            cls=plotly.utils.PlotlyJSONEncoder,
        )
    )
    assert result2[0]["props"]["header_class_name"] == "text-danger"
