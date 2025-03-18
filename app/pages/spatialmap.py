import logging
from dash import (
    Input,
    Output,
    callback,
    dcc,
    html,
    register_page,
    State,
    MATCH,
    no_update,
)
import pandas as pd
import numpy as np
from pathlib import Path
from pages.constants import FILE_DESTINATION as FD
from components import alerts
import pages.ui as ui
import math

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)


def title(block=None):
    if not block:
        return "Invalid request"
    else:
        return f"{block} Volumetric Map"


register_page(
    __name__,
    path_template="/volumetric-map/<block>",
    title=title,
)


# Initial data retrieval tasks


def make_defaults(ranges_df: pd.DataFrame) -> dict:
    defaults = {"d_scheme": "haline", "d_layer": "All", "d_category": "All"}
    d_val = ranges_df.columns[np.nonzero(ranges_df.loc["Default"])].values[0]
    defaults["d_value"] = d_val
    return defaults


def make_axes(df: pd.DataFrame) -> dict:
    axes = {}
    axis_labels = ["X", "Y", "Z"]

    for label in axis_labels:
        axis_min = df.loc[0, f"{label} Min"]
        axis_max = df.loc[0, f"{label} Max"]
        axis_step = df.loc[0, f"{label} Size"]
        axes[label] = [x for x in range(axis_min, axis_max + 1, axis_step)]

    return axes


def make_layers(z_axis: list) -> list:
    num_layers = len(z_axis) - 1
    layers = ["All"]
    more_layers = [f"Layer {x + 1}" for x in range(num_layers)]
    layers.extend(more_layers)
    return layers


def load_data(block: str) -> tuple[dict, dict, list, list, list, dict]:
    # page info dict, defaults dict, layers, category options, values, axes
    dir = f"{FD['volumetric-map']}/{block}"
    meta = pd.read_csv(f"{dir}/meta.csv")
    value_ranges = pd.read_csv(f"{dir}/value_ranges.csv", index_col="Row Label")
    category_labels = pd.read_csv(f"{dir}/category_labels.csv")
    vol_measurements = pd.read_csv(f"{dir}/vol_measurements.csv")
    downloads = pd.read_csv(f"{FD['volumetric-map']}/downloads.csv")

    # Get title and desc
    page_info = meta.iloc[0].to_dict()

    # Make defaults dict
    defaults = make_defaults(value_ranges)

    # Get axes
    axes = make_axes(vol_measurements)

    # Make layers list
    layers = make_layers(axes["Z"])

    # make category options
    category_opts = category_labels.iloc[0].to_dict()

    # get value labels and min/maxes
    value_info = value_ranges.iloc[0:2].to_dict()

    return page_info, defaults, layers, category_opts, value_info, axes, downloads


def layout(block=None, **kwargs):
    try:
        page_info, defaults, layers, category_opts, value_info, axes, downloads = (
            load_data(block)
        )
    except FileNotFoundError:
        return alerts.send_toast(
            "Cannot load page",
            "Missing required configuration, please contact an administrator to resolve the issue.",
            "failure",
        )

    values = list(value_info.keys())
    category_opts["Selected"] = defaults["d_category"]
    # value_min_max = find_global_value_bounds(value_info)

    download_content = ui.make_downloads_ui_elements(
        downloads[downloads["Block"] == block]
    )

    content = html.Div(
        children=[
            html.Section(
                id="cross-section",
                children=[
                    html.Header(html.H2(page_info["Title"])),
                    html.P(page_info["Description"]),
                    ui.make_volumetric_map_filters(defaults, layers, values),
                    html.Div(id="current-filters"),
                    ui.volumetric_map_tab_content,
                    dcc.Store(id="value-store"),
                    dcc.Store(id="color-store-sm"),
                    dcc.Store(id="cube-opacity-store-sm"),
                    dcc.Store(id="point-opacity-store-sm"),
                    dcc.Store(id="layer-store-sm"),
                    dcc.Store(id="category-selected"),
                    dcc.Store(id="category-store", data=category_opts),
                    dcc.Store(id="value-range-store", data=value_info),
                    # dcc.Store(id="value-range-store", data=value_min_max),
                    dcc.Store(id="axes-store", data=axes),
                    dcc.Store(id="block-store", data=block),
                ],
            ),
            html.Section(id="download-dataset", children=download_content),
        ]
    )
    return content


@callback(
    Output("category-selected", "data"),
    Input("categorydd", "value"),
)
def save_category_opt(data):
    return data


@callback(Output("value-store", "data"), Input("proteinsdd", "value"))
def save_protein_filter(value):
    return value


@callback(Output("color-store-sm", "data"), Input("cschemedd", "value"))
def save_color_scheme(value):
    return value


@callback(Output("layer-store-sm", "data"), Input("layersdd", "value"))
def save_layer(value):
    return value


@callback(Output("cube-opacity-store-sm", "data"), Input("cubeslider", "value"))
def save_cube_opacity(value):
    return value


@callback(Output("point-opacity-store-sm", "data"), Input("pointslider", "value"))
def save_point_opacity(value):
    return value


@callback(
    Output("extra-volumetric-map-filters", "children"),
    Input("tabs", "active_tab"),
    State("category-selected", "data"),
    State("category-store", "data"),
    State("point-opacity-store-sm", "data"),
    State("cube-opacity-store-sm", "data"),
)
def update_controls(at, category_selected, category_data, point_opacity, cube_opacity):
    if at == "layer-tab" or not at:
        return
    else:
        option_keys = list(category_data.keys())
        dd_opts = ["All"]
        for key in option_keys:
            if key != "Category" and key != "Selected":
                dd_opts.append(category_data[key])
        if at == "cube-tab":
            return [ui.make_extra_filters(at, category_selected, dd_opts, cube_opacity)]
        if at == "point-tab":
            return [
                ui.make_extra_filters(at, category_selected, dd_opts, point_opacity)
            ]
        if at == "sphere-tab":
            return [ui.make_extra_filters(at, category_selected, dd_opts)]


@callback(
    Output("volumetric-map-graph", "figure"),
    Input("tabs", "active_tab"),
    Input("color-store-sm", "data"),
    Input("value-store", "data"),
    Input("cube-opacity-store-sm", "data"),
    Input("point-opacity-store-sm", "data"),
    Input("layer-store-sm", "data"),
    Input("category-selected", "data"),
    State("category-store", "data"),
    State("value-range-store", "data"),
    State("axes-store", "data"),
    State("block-store", "data"),
)
def update_fig(
    tab,
    color="haline",
    value="",
    cubeopacity=0.4,
    pointopacity=0.1,
    layer="All",
    category_selected="All",
    category_data={},
    value_range_dict={},
    # value_ranges=(0, 1),
    axes={},
    block="",
):
    # Dash overrides the parameter defaults by passing in None sometimes, must reset defaults in that case
    props = {
        "color": color,
        "value": value,
        "cubeopacity": cubeopacity,
        "pointopacity": pointopacity,
        "layer": layer,
        "category_selected": category_selected,
    }
    settings = {
        "color": "haline",
        "value": "",
        "cubeopacity": 0.4,
        "pointopacity": 0.1,
        "layer": "All",
        "category_selected": "All",
    }
    for key in settings.keys():
        if props[key] is not None:
            settings[key] = props[key]
    value_ranges = (value_range_dict[value]["Min"], value_range_dict[value]["Max"])
    if tab == "cube-tab":
        try:
            df = pd.read_csv(f"{FD['volumetric-map']}/{block}/cube_data.csv")
        except FileNotFoundError:
            return alerts.send_toast(
                "Cannot load page",
                "Missing required configuration, please contact an administrator to resolve the issue.",
                "failure",
            )

        return ui.make_cube_fig(
            axes,
            value_ranges,
            category_data,
            df,
            colorscheme=settings["color"],
            value=settings["value"],
            opacity=settings["cubeopacity"],
            layer=settings["layer"],
            category_opt=settings["category_selected"],
        )
    elif tab == "point-tab":
        try:
            df = pd.read_csv(f"{FD['volumetric-map']}/{block}/points_data.csv")
        except FileNotFoundError:
            return alerts.send_toast(
                "Cannot load page",
                "Missing required configuration, please contact an administrator to resolve the issue.",
                "failure",
            )
        return ui.make_point_fig(
            axes,
            value_ranges,
            df,
            colorscheme=settings["color"],
            value=settings["value"],
            opacity=settings["pointopacity"],
            layer=settings["layer"],
        )
    elif tab == "layer-tab":
        try:
            df = pd.read_csv(f"{FD['volumetric-map']}/{block}/points_data.csv")
        except FileNotFoundError:
            return alerts.send_toast(
                "Cannot load page",
                "Missing required configuration, please contact an administrator to resolve the issue.",
                "failure",
            )
        return ui.make_layer_fig(
            axes,
            value_ranges,
            df,
            colorscheme=settings["color"],
            value=settings["value"],
            layer=settings["layer"],
        )
    elif tab == "sphere-tab":
        try:
            df = pd.read_csv(f"{FD['volumetric-map']}/{block}/points_data.csv")
        except FileNotFoundError:
            return alerts.send_toast(
                "Cannot load page",
                "Missing required configuration, please contact an administrator to resolve the issue.",
                "failure",
            )
        return ui.make_sphere_fig(
            axes,
            value_ranges,
            category_data,
            df,
            colorscheme=settings["color"],
            value=settings["value"],
            layer=settings["layer"],
            category_opt=settings["category_selected"],
        )


@callback(
    Output({"type": "dcc-download", "index": MATCH}, "data"),
    Input({"type": "btn-download", "index": MATCH}, "n_clicks"),
    State({"type": "btn-download", "index": MATCH}, "id"),
    prevent_initial_call=True,
)
def display_output(n_clicks, id):
    try:
        downloads = pd.read_csv(f"{FD['volumetric-map']}/downloads.csv")
    except FileNotFoundError:
        return alerts.send_toast(
            "Cannot load page",
            "Missing required configuration, please contact an administrator to resolve the issue.",
            "failure",
        )
    row = downloads.loc[id["index"]]
    file_path = Path(f"{FD['volumetric-map']}/{row['Block']}/{row['Name']}")
    if not Path.exists(file_path):
        return no_update
    return dcc.send_file(f"{FD['volumetric-map']}/{row['Block']}/{row['Name']}")
