import logging

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, dcc, html, no_update, register_page
from PIL import Image

from pages.constants import FILE_DESTINATION as FD

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)

s_imgs = pd.read_csv(FD["si-block"]["si-files"])


def title(iset=None, block=None):
    if iset:
        img = s_imgs.loc[(s_imgs["Image Set"] == iset)]
        if img.empty:
            return "Scientific Images"
        else:
            cat = img.at[img.index[0], "Image Category"]
            return f"{iset} {cat}"
    else:
        return "Scientific Images"


register_page(
    __name__,
    path_template="/scientific-images/<block>/<iset>",
    path="/scientific-images/P1-19A/P1-19A-1",
    title=title,
)


def make_tab_content(slider=False, points=0, channels=1):
    card_content = []
    body_content = [
        html.Div(
            id="si-slider-output",
            className="custom-slicer-div",
        ),
    ]

    if channels <= 1:
        # tabs element must exist so the callback will work; style hides it
        card_content.append(
            dbc.Tabs([], id="tabs", active_tab="channel-1", style={"display": "none"})
        )
    else:
        tabs = []
        for i in range(channels):
            tabs.append(dbc.Tab(label=f"Channel {i + 1}", tab_id=f"channel-{i + 1}"))
        card_content.append(
            dbc.CardHeader(
                dbc.Tabs(
                    tabs,
                    id="tabs",
                    active_tab="channel-1",
                )
            ),
        )

    if slider:
        body_content.append(
            dcc.Slider(
                1,
                points,
                1,
                value=1,
                id="si-slider",
            ),
        )

    card_content.append(dbc.CardBody(body_content))
    return dbc.Card(card_content, class_name="slicer-card")


def make_download_section(filename):
    return html.Div(
        children=[
            html.H2("Download original file", className="download-header"),
            html.P(filename),
            html.Div(
                dbc.Button(
                    "Download",
                    id="btn-download-si",
                ),
                className="download-button-container",
            ),
            dcc.Download(id="download-si"),
        ],
        style={"min-height": 155},
    )


def layout(iset=None, **kwargs):
    # handle bad image set values
    img = s_imgs.loc[(s_imgs["Image Set"] == iset)]
    if img.empty:
        return html.Div(html.P("Invalid image set requested"))

    ext_pos = img.at[img.index[0], "File"].rfind(".")
    basefile = img.at[img.index[0], "File"][0:ext_pos]

    # flatten dict since there is only one row
    img_dict = {
        "block": img.at[img.index[0], "Tissue Block"],
        "iset": img.at[img.index[0], "Image Set"],
        "cat": img.at[img.index[0], "Image Category"],
        "file": img.at[img.index[0], "File"],
        "basefile": basefile,
        "slices": img.at[img.index[0], "Slices"],
        "channels": img.at[img.index[0], "Channels"],
        "height": img.at[img.index[0], "Height"],
        "width": img.at[img.index[0], "Width"],
    }

    return html.Div(
        [
            html.Section(
                [
                    html.H2(f"{img_dict['iset']} {img_dict['cat']}"),
                    make_tab_content(
                        (img_dict["slices"] > 1),
                        img_dict["slices"],
                        img_dict["channels"],
                    ),
                    dcc.Store(id="si-slider-store"),
                    dcc.Store(id="si-file-store", data=img_dict),
                ]
            ),
            html.Section(
                [
                    make_download_section(img_dict["file"]),
                    html.Hr(),
                ]
            ),
        ]
    )


@callback(Output("si-slider-store", "data"), Input("si-slider", "value"))
def save_slider_pos(value):
    return value


@callback(
    Output("si-slider-output", "children"),
    Input("tabs", "active_tab"),
    Input("si-slider-store", "data"),
    State("si-file-store", "data"),
)
def update_pic(tab, slider, data):
    # callbacks must be included in the page even though not all layouts need them
    # no_update supresses the callback if not needed for this path
    if not tab and not slider:
        return no_update
    elif not slider:
        val_str = "0000"
    else:
        val = slider - 1
        val_str = f"{val:04}"

    if not tab:
        c = 0
    else:
        c = int(tab[-1]) - 1

    if data["file"][-3:] == "jpg":
        pic = Image.open(
            f"assets/config/scientific-images/{data['block']}/{data['basefile']}/{data["file"]}"
        )
    else:
        pic = Image.open(
            f"assets/config/scientific-images/{data['block']}/{data['basefile']}/{data['basefile']}_C{c}{val_str}.png"
        )
    # add max-height and max-width to style based on image's dimensions
    if int(data["height"]) > 600:
        ar = int(data["width"]) / int(data["height"])
        max_height = 600
        max_width = ar * 600
    else:
        max_height = int(data["height"])
        max_width = int(data["width"])

    return html.Img(
        src=pic,
        className="custom-slicer-img solo-slicer-img",
        style={"max-height": max_height, "max-width": max_width},
    )


@callback(
    Output("download-si", "data"),
    Input("btn-download-si", "n_clicks"),
    State("si-file-store", "data"),
    prevent_initial_call=True,
)
def download_file(n_clicks, data):
    app_logger.debug(f"Sending {data['file']}")
    return dcc.send_file(
        f"assets/config/scientific-images/{data['block']}/{data['basefile']}/{data['file']}"
    )
