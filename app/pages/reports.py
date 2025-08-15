import logging
import pandas as pd
import numpy as np
from dash import register_page
from pages.constants import FILE_DESTINATION as FD
from pages.ui import make_summary_grids
from components import alerts

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)


def get_reports():
    return pd.read_csv(FD["reports"]["publish"])


try:
    report_test = get_reports()
    if not report_test.empty:
        register_page(
            __name__,
            path="/reports",
            title="Reports",
        )
except Exception:
    # if there aren't any reports, this page shouldn't exist
    pass


def layout(**kwargs):
    reports = get_reports()
    app_logger.debug(f"Data columns imported for report link list:\n{reports.columns}")

    try:
        organs = reports["Organ ID"].unique()
    except KeyError:
        return alerts.send_toast(
            "Cannot load page",
            "Missing required configuration, please contact an administrator to resolve the issue.",
            "failure",
        )

    if len(organs) == 0 or np.isnan(organs).all():
        return alerts.send_toast(
            "Cannot load page",
            "Missing required configuration, please contact an administrator to resolve the issue.",
            "failure",
        )

    columns = [
        {"field": "Name", "flex": 3},
        {"field": "Link", "cellRenderer": "dsExternalLink", "flex": 1},
    ]

    return make_summary_grids(
        organs, reports, columns, "Organ ID", "Organ Description", "reports"
    )
