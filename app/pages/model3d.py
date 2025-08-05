import logging
import json
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import (
    Input,
    Output,
    State,
    callback,
    dcc,
    html,
    register_page,
    MATCH,
    callback_context,
)
from pywavefront import Wavefront
from pages.constants import FILE_DESTINATION as FD
from pages.ui import make_tabs
from pages.home import cache


register_page(__name__, path="/3d", title="3D Tissue Sample Model")

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)


def get_blocks():
    return pd.read_csv(FD["si-block"]["block-data"])


def filter_blocks(curve_number) -> tuple[str, pd.DataFrame]:
    blocks = get_blocks()
    row = blocks.loc[blocks["Tissue Block"] == curve_number]
    print("row:\n", row)
    if not row.empty:
        block_name = row.iloc[0]["Tissue Block"]
    else:
        block_name = ""
    return block_name, row


def get_organs() -> list:
    # Get organ ID's
    traces = pd.read_csv(f"{FD["obj-files"]["summary"]}/obj-files.csv")
    blocks = get_blocks()
    organs = list(traces["Organ"].unique())
    organ_descs = []
    organ_traces = []

    # Get organ descriptions and trace name
    for i in range(len(organs)):
        desc_block = blocks.loc[blocks["Organ ID"] == organs[i]]
        if desc_block.empty:
            desc = organs[i]
        else:
            desc = desc_block["Organ Description"].unique()[0]
        organ_descs.append(desc)
        this_organ = traces.loc[traces["Organ"] == organs[i]].copy()
        organ_traces.append(this_organ["Name"].to_list())

    return organ_descs, organ_traces


def get_trace(idx) -> tuple[list, list]:
    """
    Splits organ data into a separate Dataframe for each organ. This is necessary because when the traces are added to
    separate graphs per organ, Dash will restart the indexing for the traces for each graph. Since the trace index is
    the only way to identify the trace in the click data, the trace indexing needs to match in the graph and in the
    Dataframe that will be used to populate the Block Data panel.

    Returns organs, organ traces
    """
    traces = pd.read_csv(f"{FD["obj-files"]["summary"]}/obj-files.csv")

    # split data by organ for later access
    organs = list(traces["Organ"].unique())
    this_organ = traces.loc[traces["Organ"] == organs[idx]].copy()
    this_organ.index = pd.Index([x for x in range(this_organ.shape[0])])
    return this_organ


def check_null(value):
    if pd.isna(value):
        return " "
    else:
        return value


def read_obj(file: str) -> tuple[np.array, np.array]:
    """Reads an obj file at the given location and returns the vertices and faces of the object represented by the obj file."""
    organ = Wavefront(file, collect_faces=True)
    matrix_vertices = np.array(organ.vertices)
    faces = np.array(organ.mesh_list[0].faces)
    app_logger.debug(
        f"Read {file} and found vertices ndarray of shape {matrix_vertices.shape} and faces ndarray of shape {faces.shape}"
    )
    return matrix_vertices, faces


def make_mesh_settings(
    vertices: np.array,
    faces: np.array,
    name: str,
    color="cyan",
    opacity=1,
    x_map="x",
    y_map="y",
    z_map="z",
) -> list[object]:
    """
    Populates a 3d mesh object for use with Plotly Dash graph objects
    """
    coord_pos = {"x": 0, "y": 1, "z": 2}

    # with default settings, vertices.T has x, y, z in that order
    x = vertices.T[coord_pos[x_map]]
    y = vertices.T[coord_pos[y_map]]
    z = vertices.T[coord_pos[z_map]]

    L, M, N = faces.T

    mesh = {
        "type": "mesh3d",
        "x": x,
        "y": y,
        "z": z,
        "color": color,
        "flatshading": False,
        "opacity": opacity,
        "i": L,
        "j": M,
        "k": N,
        "name": name,
        "showscale": None,
        "lighting": {
            "ambient": 0.18,
            "diffuse": 1,
            "fresnel": 0.1,
            "specular": 1,
            "roughness": 0.1,
            "facenormalsepsilon": 1e-6,
            "vertexnormalsepsilon": 1e-12,
        },
        "lightposition": {"x": 100, "y": 200, "z": 0},
    }

    return [mesh]


def make_mesh_data(
    name: str, file: str, color=None, opacity=1, x_map="x", y_map="y", z_map="z"
) -> object:
    """
    Reads an obj file and populates a 3d mesh object.
    """
    vertices, faces = read_obj(file)
    data = make_mesh_settings(
        vertices,
        faces,
        name,
        color=color,
        opacity=opacity,
        x_map=x_map,
        y_map=y_map,
        z_map=z_map,
    )
    data[0]["name"] = name
    return data


@cache.memoize()
def make_mesh_fig(idx=0) -> go.Figure:
    """Plots the objects described in an obj in a Plotly Dash figure"""
    organ_trace = get_trace(idx)
    if organ_trace.shape[0] == 0:
        return
    start = True
    for i in organ_trace.index:
        try:
            file_loc = f"{FD["obj-files"]["volumes"]}/{organ_trace.at[i, "File"]}"
            if start:
                data1 = make_mesh_data(
                    organ_trace.at[i, "Name"],
                    file_loc,
                    organ_trace.at[i, "Color"],
                    organ_trace.at[i, "Opacity"],
                    organ_trace.at[i, "x axis"],
                    organ_trace.at[i, "y axis"],
                    organ_trace.at[i, "z axis"],
                )
                fig = go.Figure(data1)
                name = data1[0]["name"]
                app_logger.debug(f"Added trace for {name} to 3D Model of organ {idx}")
                start = False
            else:
                data = make_mesh_data(
                    organ_trace.at[i, "Name"],
                    file_loc,
                    organ_trace.at[i, "Color"],
                    organ_trace.at[i, "Opacity"],
                    organ_trace.at[i, "x axis"],
                    organ_trace.at[i, "y axis"],
                    organ_trace.at[i, "z axis"],
                )
                fig.add_trace(go.Mesh3d(data[0]))
                name = data[0]["name"]
                app_logger.debug(f"Added trace for {name} to 3D Model of organ {idx}")
        except FileNotFoundError:
            # try to add the other traces
            continue
    try:
        fig.update_layout(
            scene_aspectmode="data",
            height=500,
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
            ),
            margin=dict(l=20, r=20, t=20, b=20),
        )
        return fig
    # This means none of the traces were added
    except UnboundLocalError:
        return False


def make_graph_layout(organ=1, idx=0) -> html.Section:
    fig = make_mesh_fig(idx)
    if not fig:
        card_content = "No models could be loaded for this organ"
    else:
        card_content = dcc.Graph(
            id={"type": "organ-graph", "index": idx},
            figure=fig,
            config={"scrollZoom": False},
            className="centered-graph",
        )
    data = [
        dbc.Row(dbc.Col(html.Header(html.H2(f"3D Model of {organ}")))),
        dbc.Row(
            [
                dbc.Col(
                    [dbc.Card(card_content)],
                    width=9,
                ),
                dbc.Col(
                    dbc.Card(
                        id={"type": "click-data", "index": idx},
                        color="light",
                        class_name="block-card",
                    ),
                    width=3,
                ),
            ],
            className="g-3",
        ),
    ]
    if idx == 0:
        container = html.Section(data)
    else:
        container = html.Section(data, className="middle-section")
    return container


def layout(**kwargs):
    organ_descs, organ_traces = get_organs()
    if len(organ_traces) == 0:
        return html.Div("No 3D models have been loaded.")
    # add a tab for each organ
    tab_list = []
    for i in range(len(organ_descs)):
        this_organ = (f"tab-{i}", organ_descs[i])
        tab_list.append(this_organ)

    tab_area = dbc.Card(
        [
            make_tabs(
                "model-tabs",
                "tab-0",
                tab_list,
            ),
            dbc.CardBody([html.Div(id="model-fig")]),
        ]
    )
    # save state
    return html.Div(
        children=[
            html.Div(tab_area),
            dcc.Store(id="organ-descs", data=json.dumps(organ_descs)),
            dcc.Store("organ-traces", data=json.dumps(organ_traces)),
        ]
    )


@callback(
    Output({"type": "click-data", "index": MATCH}, "children"),
    Input({"type": "organ-graph", "index": MATCH}, "clickData"),
    State("organ-traces", "data"),
)
def display_click_data(click_data, organ_traces):
    blank_content = "Click on a block to view available datasets"
    blank_card_content = [
        dbc.CardHeader("Block Data"),
        dbc.CardBody(
            [
                html.P(blank_content),
            ],
        ),
    ]
    if click_data:
        input_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        idx = int(json.loads(input_id)["index"])
        organ_traces_list = json.loads(organ_traces)
        block_name, row = filter_blocks(
            organ_traces_list[idx][click_data["points"][0]["curveNumber"]]
        )
        if row.empty:
            return blank_card_content
        app_logger.debug(f"Displaying click data for {block_name}")
        card_content = [
            dbc.CardHeader(
                "Block" + " " + str(row.iloc[0]["Tissue Block"]),
                class_name="card-title",
            )
        ]
        card_body_content = []
        data_options = {
            "Anatomical region: ": "Anatomical region",
            "View scientific images": "Images",
            "View reports": "Reports",
            "View volumetric map": "Volumetric Map",
        }
        for key in data_options.keys():
            if check_null(row.iloc[0][data_options[key]]) != " ":
                if key == "Anatomical region: ":
                    child = html.P(key + row.iloc[0][data_options[key]])
                    card_body_content.append(child)
                else:
                    value_str = row.iloc[0][data_options[key]]
                    child = html.P([dcc.Link(key, href=f"{value_str}")])
                    card_body_content.append(child)
        card_content.append(dbc.CardBody(card_body_content))
        return card_content
    else:
        return blank_card_content


@callback(
    Output("model-fig", "children"),
    Input("model-tabs", "active_tab"),
    State("organ-descs", "data"),
)
def update_fig(tab, organ_descs):
    # get index from tab id
    idx = int(tab[-1])
    descs = json.loads(organ_descs)
    organ_desc = descs[idx]
    return make_graph_layout(organ=organ_desc, idx=idx)
