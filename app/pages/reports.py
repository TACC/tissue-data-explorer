import logging

import dash_ag_grid as dag
import pandas as pd
from dash import html, register_page
from pages.constants import FILE_DESTINATION as FD

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)


try:
    reports = pd.read_csv(FD["reports"]["publish"])
    if not reports.empty:
        register_page(
            __name__,
            path="/reports",
            title="Reports",
        )
except Exception:
    # if there aren't any reports, this page shouldn't exist
    pass


def layout(**kwargs):
    app_logger.debug(f"Data columns imported for report link list:\n{reports.columns}")

    columns = [
        {"field": "Name", "flex": 3},
        {"field": "Link", "cellRenderer": "dsExternalLink", "flex": 1},
    ]

    rows = reports.to_dict("records")
    height = len(rows) * 41.25 + 49 + 15

    grid = dag.AgGrid(
        id="geo-reports-grid",
        rowData=rows,
        columnDefs=columns,
        className="ag-theme-alpine block-grid",
        columnSize="sizeToFit",
        style={"height": height},
    )

    return html.Div(
        html.Section(
            children=[
                html.Header(html.H2("Reports")),
                grid,
            ],
        )
    )
