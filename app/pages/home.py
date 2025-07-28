import logging

import dash_ag_grid as dag
import pandas as pd
from dash import html, register_page, get_app
from components import alerts
from pages.constants import FILE_DESTINATION as FD
from flask_caching import Cache

register_page(__name__, path="/")

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)


# set up cache
app = get_app()
cache = Cache(app.server)
cache.init_app(app.server)


def read_blocks():
    return pd.read_csv(FD["si-block"]["block-data"])


def make_grid(blocks, columns, organ="P1"):
    o = blocks.loc[blocks["Organ ID"] == organ]
    orows = o.to_dict("records")
    oheight = len(orows) * 41.25 + 49 + 15

    return dag.AgGrid(
        id=f"{organ}-df",
        rowData=orows,
        columnDefs=columns,
        className="ag-theme-alpine block-grid",
        columnSize="sizeToFit",
        style={"height": oheight},
    )


def layout():
    try:
        blocks = read_blocks()
    except FileNotFoundError:
        return alerts.send_toast(
            "Cannot load page",
            "Missing required configuration, please contact an administrator to resolve the issue.",
            "failure",
        )

    organs = blocks["Organ ID"].unique()
    if len(organs) == 0:
        return html.Div("No dataset metadata has been loaded.")

    app_logger.debug(f"Data columns imported for home page grid:\n{blocks.columns}")

    columns = [
        {"field": "Order"},
        {"field": "Tissue Block"},
        {"field": "Anatomical region"},
        {"field": "Images", "cellRenderer": "dsLink"},
        {"field": "Reports", "cellRenderer": "dsLink"},
        {"field": "Volumetric Map", "cellRenderer": "dsLink"},
    ]

    # if no rows have a value for a certain content type, leave that column out
    with_content = [
        blocks.loc[blocks["Images"] != " "],
        blocks.loc[blocks["Reports"] != " "],
        blocks.loc[blocks["Volumetric Map"] != " "],
    ]

    k = 0
    for j in range(3):
        if with_content[j].empty:
            del columns[k + 3]
        else:
            k += 1

    sections = []
    for organ in organs:
        organ_data = blocks.loc[blocks["Organ ID"] == organ]
        if not organ_data.empty:
            # assumes they have set the organ description consistently
            organ_desc = organ_data.at[organ_data.index[0], "Organ Description"]
            if len(sections) == 0:
                section = html.Section(
                    [
                        html.Header(html.H2(f"{organ_desc} Datasets")),
                        make_grid(blocks, columns, organ),
                    ]
                )
            else:
                section = html.Section(
                    [
                        html.Header(
                            html.H2(f"{organ_desc} Datasets"),
                            className="middle-section",
                        ),
                        make_grid(blocks, columns, organ),
                    ]
                )
            sections.append(section)
    return html.Div(sections)
