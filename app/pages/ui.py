from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_ag_grid as dag
from pages.constants import FILE_DESTINATION as FD

C_SCHEMES = [
    "bluered",
    "deep",
    "delta",
    "greys",
    "haline",
    "ice",
    "inferno",
    "jet",
    "magma",
    "plasma",
    "spectral",
    "thermal",
    "viridis",
    "ylgnbu",
    "ylorrd",
]


# summary page functions
def make_grid(df, columns, which_grid, organ="P1"):
    o = df.loc[df["Organ ID"] == organ]
    orows = o.to_dict("records")
    oheight = len(orows) * 41.25 + 49 + 15

    return dag.AgGrid(
        id=f"{organ}-{which_grid.lower()}-df",
        rowData=orows,
        columnDefs=columns,
        className="ag-theme-alpine block-grid",
        columnSize="sizeToFit",
        style={"height": oheight},
    )


def make_summary_grids(organs, df, columns, key, desc, which_grid):
    sections = []
    for organ in organs:
        organ_data = df.loc[df[key] == organ]
        if not organ_data.empty:
            # assumes they have set the organ description consistently
            organ_desc = organ_data.at[organ_data.index[0], desc]
            if len(sections) == 0:
                header = html.Header(html.H2(f"{organ_desc} {which_grid.capitalize()}"))
            else:
                header = html.Header(
                    html.H2(f"{organ_desc} {which_grid.capitalize()}"),
                    className="middle-section",
                )
            section = html.Section(
                [
                    header,
                    make_grid(df, columns, which_grid, organ),
                ]
            )
            sections.append(section)
    return html.Div(sections)


# generic layout functions
def make_tabs(id: str, active: str, tabs: list) -> object:
    """
    "tabs" is a list of tuples, with each tuple containing the tab label and id
    """
    tab_objs = []
    for i in range(len(tabs)):
        new_tab = dbc.Tab(tab_id=tabs[i][0], label=tabs[i][1])
        tab_objs.append(new_tab)
    tab_group = dbc.Tabs(tab_objs, id=id, active_tab=active)
    return dbc.CardHeader(tab_group)


# Volumetric map layout functions
def make_volumetric_map_filters(defaults: dict, layers: dict, values: list):
    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P("Select a protein:", className="card-text"),
                            dcc.Dropdown(
                                values,
                                defaults["d_value"],
                                id="proteinsdd",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.P("Choose a color scheme:", className="card-text"),
                            dcc.Dropdown(
                                C_SCHEMES,
                                defaults["d_scheme"],
                                id="cschemedd",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.P("Choose a layer:", className="card-text"),
                            dcc.Dropdown(
                                layers,
                                defaults["d_layer"],
                                id="layersdd",
                            ),
                        ]
                    ),
                ],
                justify="center",
            ),
        ),
        color="light",
        class_name="volumetric-map-filter",
    )


def make_downloads_ui_elements(downloads: pd.DataFrame) -> list:
    download_items = [html.Header(html.H2("Download Data Here"))]
    for i in downloads.index:
        download_items.append(html.P(downloads.loc[i, "Desc"]))
        download_items.append(
            html.Div(
                dbc.Button(
                    downloads.loc[i, "Label"], id={"type": "btn-download", "index": i}
                ),
                className="download-button-container",
            ),
        )
        download_items.append(dcc.Download(id={"type": "dcc-download", "index": i}))
        download_items.append(html.Hr())
    return download_items


def make_loader(elem):
    return dcc.Loading(
        elem,
        style={
            "visibility": "visible",
            "backgroundColor": "transparent",
            "opacity": 0.7,
        },
        type="dot",
        parent_className="loader-wrapper",
    )


volumetric_map_fig = dbc.Row(
    dbc.Col(
        dcc.Graph(
            figure={},
            className="dcc-graph",
            id="volumetric-map-graph",
        )
    )
)


def get_image_info(block):
    try:
        img_info = pd.read_csv(f"{FD["image-layer"]}/images.csv")
        # filter to just the relevant block
        img_info = img_info.loc[img_info["Block"] == block]
        if img_info.size != 0:
            img_info = img_info.sort_values(by=["Z Center"])
        return img_info
    except FileNotFoundError:
        return False


def make_volumetric_map_tab_content(block):
    tabs = []
    # find out if image layers have been loaded for this block
    image_info = get_image_info(block)
    if type(image_info) is not pd.DataFrame:
        tabs = [
            ("cube-tab", "Cube View"),
            ("point-tab", "Point View"),
            ("layer-tab", "Layer View"),
            ("sphere-tab", "Sphere View"),
        ]
    else:
        tabs = [
            ("cube-tab", "Cube View"),
            ("cube-image-tab", "Cube View with Images"),
            ("point-tab", "Point View"),
            ("layer-tab", "Layer View"),
            ("image-layer-tab", "Image Layer View"),
            ("sphere-tab", "Sphere View"),
        ]

    return dbc.Card(
        [
            make_tabs(
                "volumetric-tabs",
                "cube-tab",
                tabs,
            ),
            dbc.CardBody(
                [
                    volumetric_map_fig,
                    html.Div(id="volumetric-map-fig"),
                    html.Div(id="extra-volumetric-map-filters"),
                ]
            ),
        ]
    )


def make_opacity_slider(id, opacity):
    return [
        html.P("Adjust the opacity of the model:"),
        dcc.Slider(
            0,
            1,
            0.2,
            value=opacity,
            id=id,
        ),
    ]


def make_category_slider(start="All", category_options=["All"]):
    return [
        html.P("Select tissue:", className="card-text"),
        dcc.Dropdown(
            category_options,
            start,
            id="categorydd",
        ),
    ]


def make_image_layer_dd(start="All", layers=["All"]):
    return [
        html.P("Choose an image:", className="card-text"),
        dcc.Dropdown(
            layers,
            start,
            id="imagelayersdd",
        ),
    ]


def make_extra_filters(
    tab,
    category_opt="All",
    category_dd_opts=["All"],
    image_layer_opt="All",
    image_layer_opts=["All"],
    opacity=0.4,
    image_opacity=1,
):
    controls = []
    if tab == "cube-tab":
        controls = [
            dbc.Col(
                children=make_category_slider(category_opt, category_dd_opts),
                width=6,
                lg=4,
            ),
            dbc.Col(children=make_opacity_slider("cubeslider", opacity), width=6, lg=8),
        ]
    elif tab == "cube-image-tab":
        controls = [
            dbc.Col(
                children=make_category_slider(category_opt, category_dd_opts),
                width=2,
                lg=3,
            ),
            dbc.Col(
                children=make_image_layer_dd(image_layer_opt, image_layer_opts),
                width=2,
                lg=3,
            ),
            dbc.Col(children=make_opacity_slider("cubeslider", opacity), width=6, lg=6),
        ]
    elif tab == "point-tab":
        controls = [
            dbc.Col(
                children=make_opacity_slider("pointslider", opacity),
                width=12,
            ),
        ]
    elif tab == "image-layer-tab":
        controls = [
            dbc.Col(
                children=make_image_layer_dd(image_layer_opt, image_layer_opts),
                width=2,
                lg=3,
            ),
            dbc.Col(
                children=make_opacity_slider("imageslider", image_opacity),
                width=9,
            ),
        ]
    elif tab == "sphere-tab":
        controls = [
            dbc.Col(
                children=make_category_slider(category_opt, category_dd_opts),
            ),
        ]

    return dbc.Card(
        dbc.CardBody(
            dbc.Row(children=controls),
        ),
        color="light",
    )


# Graph functions
def select_layer(zlayer: str, df: pd.DataFrame, z_axis: list):
    if zlayer == "All":
        return df
    else:
        # get layer num
        layer = int(zlayer[-1])
        lower = z_axis[layer - 1]
        upper = z_axis[layer]
        return df[(df["Z Center"] >= lower) & (df["Z Center"] < upper)]


def select_category(category_opt, category_labels, df):
    if category_opt == "All":
        return df
    elif category_opt == category_labels["Label (Only True)"]:
        return df[df["Category"]]
    elif category_opt == category_labels["Label (Only False)"]:
        return df[~df["Category"]]


def set_layout(fig, axes):
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                nticks=10,
                range=[axes["X"][0], axes["X"][-1]],
            ),
            yaxis=dict(
                nticks=6,
                range=[axes["Y"][0], axes["Y"][-1]],
            ),
            zaxis=dict(
                nticks=5,
                range=[axes["Z"][0], axes["Z"][-1]],
            ),
            aspectmode="manual",
            aspectratio=dict(x=0.9, y=0.5, z=0.4),
            camera=dict(eye=dict(x=0.7, y=0.7, z=0.7)),
        ),
    )


def get_colors(df, value, y_axis):
    colors = []
    for i in range(len(y_axis) - 1):
        colors.append(
            df[(df["Y Center"] >= y_axis[i]) & (df["Y Center"] < y_axis[i + 1])]
            .loc[:, value]
            .to_list(),
        )
    return colors


def gen_cube_triangles(df: pd.DataFrame) -> np.ndarray:
    # In the dataset, within each set of points representing a cube, the points are ordered as follows:
    # [
    #     [x, y, z],
    #     [x + x_dist, y, z],
    #     [x, y + y_dist, z],
    #     [x + x_dist, y + y_dist, z],
    #     [x, y, z + z_dist],
    #     [x + x_dist, y, z + z_dist],
    #     [x, y + y_dist, z + z_dist],
    #     [x + x_dist, y + y_dist, z + z_dist],
    # ]

    triangle_pattern = [
        [0, 1, 2],
        [0, 1, 4],
        [0, 2, 4],
        [4, 5, 1],
        [4, 2, 6],
        [4, 5, 6],
        [3, 2, 6],
        [3, 5, 1],
        [3, 2, 1],
        [7, 6, 5],
        [7, 6, 3],
        [7, 3, 5],
    ]

    all_triangles = []

    for m in range(0, df.shape[0], 8):
        all_triangles.extend([[m + x[0], m + x[1], m + x[2]] for x in triangle_pattern])

    faces1 = np.array(all_triangles)
    return np.transpose(faces1)


def make_point_fig(
    axes,
    value_ranges,
    df,
    opacity=0.1,
    colorscheme="haline",
    value="",
    layer="All",
):
    """Create figure for point view of volumetric map data"""
    df4 = select_layer(layer, df, axes["Z"])
    X = df4.loc[:, "X Center"]
    Y = df4.loc[:, "Y Center"]
    Z = df4.loc[:, "Z Center"]
    values = df4.loc[:, value]

    fig2 = go.Figure(
        data=go.Volume(
            x=X,
            y=Y,
            z=Z,
            value=values,
            isomin=value_ranges[0],
            isomax=value_ranges[1],
            opacity=opacity,
            colorscale=colorscheme,
            surface_count=21,
            name="Point View",
        )
    )

    set_layout(fig2, axes)
    return fig2


def make_layer_fig(
    axes,
    value_ranges,
    df,
    colorscheme="haline",
    value="",
    layer="All",
):
    """Create figure for layer view of volumetric map data"""
    data = []

    if layer == "All":
        for k in range(len(axes["Z"]) - 1):
            this_layer = select_layer(f"Layer {k + 1}", df, axes["Z"])
            color_set = get_colors(this_layer, value, axes["Y"])
            X = this_layer.loc[:, "X Center"].unique()
            Y = this_layer.loc[:, "Y Center"].unique()
            z_val = this_layer.loc[:, "Z Center"].unique()[0]
            Z = [[z_val for i in X] for j in Y]
            if k == 0:
                data.append(
                    go.Surface(
                        x=X,
                        y=Y,
                        z=Z,
                        colorscale=colorscheme,
                        surfacecolor=color_set,
                        name=f"Layer {k + 1}",
                        cmin=value_ranges[0],
                        cmax=value_ranges[1],
                    ),
                )
            else:
                data.append(
                    go.Surface(
                        x=X,
                        y=Y,
                        z=Z,
                        colorscale=colorscheme,
                        surfacecolor=color_set,
                        name=f"Layer {k + 1}",
                        cmin=value_ranges[0],
                        cmax=value_ranges[1],
                        showscale=False,
                    ),
                )
    else:
        this_layer = select_layer(layer, df, axes["Z"])
        color_set = get_colors(this_layer, value, axes["Y"])
        X = this_layer.loc[:, "X Center"].unique()
        Y = this_layer.loc[:, "Y Center"].unique()
        z_val = this_layer.loc[:, "Z Center"].unique()[0]
        Z = [[z_val for i in X] for j in Y]
        data.append(
            go.Surface(
                x=X,
                y=Y,
                z=Z,
                colorscale=colorscheme,
                surfacecolor=color_set,
                name=layer,
                cmin=value_ranges[0],
                cmax=value_ranges[1],
            ),
        )

    fig = go.Figure(data=data)
    set_layout(fig, axes)
    return fig


def make_image_layer_fig(
    axes,
    image_layer="All",
    metadata=None,
    imgs: list = None,
    colorscale=None,
    opacity=1,
):
    """Create figure for layer view of volumetric map data"""

    colors = get_colorscale(colorscale)
    data = []
    z_values = list(metadata["Z Center"])

    if image_layer == "All":
        for img, z_val in zip(imgs, z_values):
            surface = make_image_layer(
                img, z_val, axes, colors, showscale=True, opacity=opacity
            )
            data.append(surface)
    else:
        idx = int(image_layer[-1]) - 1
        surface = make_image_layer(
            imgs[idx], z_values[idx], axes, colors, showscale=True, opacity=opacity
        )
        data.append(surface)

    fig = go.Figure(data=data)

    fig.update_layout(
        scene=dict(
            aspectmode="data",
        ),
    )

    return fig


def make_sphere(x, y, z, radius, resolution=5):
    """Calculate the coordinates to plot a sphere with center at (x, y, z). Returns three Numpy ndarrays."""
    u, v = np.mgrid[0 : 2 * np.pi : resolution * 2j, 0 : np.pi : resolution * 1j]
    X = radius * np.cos(u) * np.sin(v) + x
    Y = radius * np.sin(u) * np.sin(v) + y
    Z = radius * np.cos(v) + z
    return (X, Y, Z)


def make_sphere_fig(
    axes,
    value_ranges,
    category_labels,
    df,
    opacity=1,
    colorscheme="haline",
    value="",
    layer="All",
    category_opt="All",
):
    """Create figure for sphere view of volumetric map data"""
    res = 5
    data = []

    layer_df = select_layer(layer, df, axes["Z"])
    layer_df = select_category(category_opt, category_labels, layer_df)

    scalebar = False
    for k in layer_df.index:
        s_color = layer_df.loc[k, value]
        if not np.isnan(s_color):
            (X, Y, Z) = make_sphere(
                x=layer_df.loc[k, "X Center"],
                y=layer_df.loc[k, "Y Center"],
                z=layer_df.loc[k, "Z Center"],
                radius=14,
                resolution=res,
            )
            c = [[s_color.item() for i in range(res)] for j in range(res * 2)]
            if not scalebar:
                data.append(
                    go.Surface(
                        x=X,
                        y=Y,
                        z=Z,
                        surfacecolor=c,
                        colorscale=colorscheme,
                        cmin=value_ranges[0],
                        cmax=value_ranges[1],
                        opacity=opacity,
                        name=f"val:\n{s_color.item()}",
                    )
                )
                scalebar = True
            else:
                data.append(
                    go.Surface(
                        x=X,
                        y=Y,
                        z=Z,
                        surfacecolor=c,
                        colorscale=colorscheme,
                        cmin=value_ranges[0],
                        cmax=value_ranges[1],
                        showscale=False,
                        opacity=opacity,
                        name=f"val:\n{s_color.item()}",
                    )
                )

    fig4 = go.Figure(data=data)
    set_layout(fig4, axes)
    return fig4


def make_cube_fig(
    axes,
    value_ranges,
    category_labels,
    df,
    opacity=0.4,
    colorscheme="haline",
    value="",
    layer="All",
    category_opt="All",
):
    """Create figure for cube view of volumetric map data"""
    df2 = select_layer(layer, df, axes["Z"])
    df3 = select_category(category_opt, category_labels, df2)

    X = df3.loc[:, "X Center"]
    Y = df3.loc[:, "Y Center"]
    Z = df3.loc[:, "Z Center"]
    values = df3.loc[:, value]

    faces = gen_cube_triangles(df3)

    fig1 = go.Figure(
        data=go.Mesh3d(
            x=X,
            y=Y,
            z=Z,
            i=faces[0],
            j=faces[1],
            k=faces[2],
            intensity=values,
            opacity=opacity,
            colorscale=colorscheme,
            cmin=value_ranges[0],
            cmax=value_ranges[1],
        )
    )

    set_layout(fig1, axes)
    return fig1


def make_image_layer(img, z_val, axes, colors, showscale=False, opacity=1):
    sm_df = pd.DataFrame(data=img)
    Z1 = [[z_val for j in sm_df.columns] for k in sm_df.index.values]
    surface = go.Surface(
        x=[axes["X"][0] + m for m in sm_df.columns.values],
        y=[axes["Y"][0] + n for n in sm_df.index.values],
        z=Z1,
        surfacecolor=sm_df.values,
        colorscale=colors,
        showscale=showscale,
        opacity=opacity,
    )
    return surface


def get_colorscale(scale):
    if scale:
        return scale
    else:
        return "greys"


def make_cube_image_fig(
    axes,
    value_ranges,
    category_labels,
    df,
    opacity=0.4,
    colorscheme="haline",
    value="",
    layer="All",
    image_layer="All",
    category_opt="All",
    metadata=None,
    imgs=None,
    colorscale=None,
):
    """Create figure for cube view of volumetric map data"""
    df2 = select_layer(layer, df, axes["Z"])
    df3 = select_category(category_opt, category_labels, df2)

    X = df3.loc[:, "X Center"]
    Y = df3.loc[:, "Y Center"]
    Z = df3.loc[:, "Z Center"]
    values = df3.loc[:, value]

    faces = gen_cube_triangles(df3)

    colors = get_colorscale(colorscale)

    data = []
    data.append(
        go.Mesh3d(
            x=X,
            y=Y,
            z=Z,
            i=faces[0],
            j=faces[1],
            k=faces[2],
            intensity=values,
            opacity=opacity,
            # colorbar=dict(orientation="h"),
            colorscale=colorscheme,
            cmin=value_ranges[0],
            cmax=value_ranges[1],
        )
    )

    z_values = list(metadata["Z Center"])

    if image_layer == "All":
        for img, z_val in zip(imgs, z_values):
            surface = make_image_layer(img, z_val, axes, colors)
            data.append(surface)
    else:
        idx = int(image_layer[-1]) - 1
        surface = make_image_layer(imgs[idx], z_values[idx], axes, colors)
        data.append(surface)

    fig1 = go.Figure(data=data)
    set_layout(fig1, axes)
    return fig1
