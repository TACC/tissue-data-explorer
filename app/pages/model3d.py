import logging
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html, register_page, ALL
from pywavefront import Wavefront

from pages.constants import FILE_DESTINATION as FD

register_page(__name__, path="/3d", title="3D Tissue Sample Model")

app_logger = logging.getLogger(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app_logger.handlers = gunicorn_logger.handlers
app_logger.setLevel(gunicorn_logger.level)

blocks = pd.read_csv(FD["si-block"]["block-data"])
traces = pd.read_csv(f"{FD["obj-files"]["summary"]}/obj-files.csv")


def read_obj(file):
    organ = Wavefront(file, collect_faces=True)
    matrix_vertices = np.array(organ.vertices)
    faces = np.array(organ.mesh_list[0].faces)
    app_logger.debug(
        f"Read {file} and found vertices ndarray of shape {matrix_vertices.shape} and faces ndarray of shape {faces.shape}"
    )
    return matrix_vertices, faces


def make_mesh_settings(
    vertices,
    faces,
    name,
    color="cyan",
    opacity=1,
):
    x, y, z = vertices.T
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


def make_mesh_data(name, file, color=None, opacity=1):
    vertices, faces = read_obj(file)
    data = make_mesh_settings(vertices, faces, name, color=color, opacity=opacity)
    data[0]["name"] = name
    return data


def make_mesh_fig(organ=1):
    organ_traces = traces.loc[traces["Organ"] == organ]
    if organ_traces.shape[0] == 0:
        return
    start = True
    for i in organ_traces.index:
        try:
            file_loc = f"{FD["obj-files"]["volumes"]}/{organ_traces.at[i, "File"]}"
            if start:
                data1 = make_mesh_data(
                    organ_traces.at[i, "Name"],
                    file_loc,
                    organ_traces.at[i, "Color"],
                    organ_traces.at[i, "Opacity"],
                )
                fig = go.Figure(data1)
                name = data1[0]["name"]
                app_logger.debug(f"Added trace for {name} to 3D Model of {organ}")
                start = False
            else:
                data = make_mesh_data(
                    organ_traces.at[i, "Name"],
                    file_loc,
                    organ_traces.at[i, "Color"],
                    organ_traces.at[i, "Opacity"],
                )
                fig.add_trace(go.Mesh3d(data[0]))
                name = data[0]["name"]
                app_logger.debug(f"Added trace for {name} to 3D Model of {organ}")
        except FileNotFoundError:
            # try to add the other traces
            continue
    try:
        fig.update_layout(
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


def make_graph_layout(organ=1, idx=0):
    fig = make_mesh_fig(organ)
    if not fig:
        card_content = "No models could be loaded for this organ"
    else:
        card_content = dcc.Graph(
            id={"type": "organ-graph", "index": idx},
            figure=fig,
            config={"scrollZoom": False},
            className="centered-graph",
        )
    container = html.Section(
        [
            dbc.Row(dbc.Col(html.Header(html.H2(f"3D Model of {organ}")))),
            dbc.Row(
                [
                    dbc.Col(
                        [dbc.Card(card_content)],
                        width=9,
                    ),
                    dbc.Col(
                        dbc.Card(
                            id="click-data",
                            color="light",
                            class_name="block-card",
                        ),
                        width=3,
                    ),
                ],
                className="g-3",
            ),
        ],
    )
    return container


def layout(**kwargs):
    # get unique organs from traces
    organs = list(traces["Organ"].unique())
    if len(organs) == 0:
        return html.Div("No 3D models have been loaded.")
    # add a model for each
    graphs = []
    for i in range(len(organs)):
        graphs.append(make_graph_layout(organs[i], i))
    return html.Div(graphs)


@callback(
    Output("click-data", "children"),
    Input({"type": "organ-graph", "index": ALL}, "clickData"),
)
def display_click_data(click_data):
    blank_content = "Click on a block to view available datasets"
    blank_card_content = [
        dbc.CardHeader("Block Data"),
        dbc.CardBody(
            [
                html.P(blank_content),
            ],
        ),
    ]
    if click_data and click_data[0]:
        row = blocks.loc[
            blocks["Tissue Block"]
            == traces.loc[click_data[0]["points"][0]["curveNumber"], "Name"]
        ]
        if row.empty:
            return blank_card_content
        block_name = row.iloc[0]["Tissue Block"]
        app_logger.debug(f"Displaying click data for {block_name}")
        item_data = [
            {"label": "Block ", "value": row.iloc[0]["Tissue Block"]},
            {"label": "Anatomical region: ", "value": row.iloc[0]["Anatomical region"]},
            {
                "label": "View scientific images",
                "value": row.iloc[0]["Images"],
            },
            {"label": "View reports", "value": row.iloc[0]["Reports"]},
            {"label": "View volumetric map", "value": row.iloc[0]["Volumetric Map"]},
        ]
        card_content = []
        card_body_content = []
        for i in range(5):
            label_str = str(item_data[i]["label"])
            value_str = str(item_data[i]["value"])
            if i == 0:
                card_content.append(
                    dbc.CardHeader(label_str + value_str, class_name="card-title")
                )
            elif i == 1:
                child = html.P(label_str + value_str)
                card_body_content.append(child)
            elif item_data[i]["value"] == " ":
                continue
            else:
                value_str = item_data[i]["value"]
                child = html.P([dcc.Link(label_str, href=f"{value_str}")])
                card_body_content.append(child)
        card_content.append(dbc.CardBody(card_body_content))
        return card_content
    else:
        return blank_card_content
