import logging

import dash_ag_grid as dag
import pandas as pd
from dash import html, register_page
from components import alerts
from pages.constants import FILE_DESTINATION as FD

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)


def title(block=None):
    return f"{block} scientific images"


register_page(
    __name__,
    path_template="/scientific-images-list/<block>",
    path="/scientific-images-list/P1-19A",
    title=title,
)


def layout(block=None, **kwargs):
    try:
        thumbnails = pd.read_csv(FD["thumbnails"]["catalog"])
    except FileNotFoundError:
        return alerts.send_toast(
            "Cannot load page",
            "Missing required configuration, please contact an administrator to resolve the issue.",
            "failure",
        )
    app_logger.debug(
        f"Data columns imported for scientific image file summary:\n{thumbnails.columns}"
    )

    block_thumbnails = thumbnails.loc[thumbnails["Block"] == block]

    columns = [
        {
            "field": "Preview",
            "cellRenderer": "previewImg",
            "flex": 2,
            "cellClass": "center-aligned-cell",
            "headerClass": "center-aligned-header ag-header-cell-label",
        },
        {"field": "Name", "flex": 3},
        {"field": "Link", "cellRenderer": "dsLink", "flex": 1},
    ]

    grid = dag.AgGrid(
        id="oc-files-grid",
        rowData=block_thumbnails.to_dict("records"),
        columnDefs=columns,
        className="ag-theme-alpine block-grid large",
        style={"height": 700},
    )

    return html.Div(
        html.Section(
            children=[
                html.Header(html.H2(f"{block} Scientific Image Sets")),
                grid,
            ],
        )
    )
