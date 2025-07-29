import logging
import pandas as pd
from dash import html, register_page
from pages.constants import FILE_DESTINATION as FD
from pages.ui import make_summary_grids

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

    organs = reports["Organ ID"].unique()
    if len(organs) == 0:
        return html.Div("No dataset metadata has been loaded.")

    columns = [
        {"field": "Name", "flex": 3},
        {"field": "Link", "cellRenderer": "dsExternalLink", "flex": 1},
    ]

    return make_summary_grids(
        organs, reports, columns, "Organ ID", "Organ Description", "reports"
    )
