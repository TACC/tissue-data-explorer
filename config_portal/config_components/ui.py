from dash import html, dcc
import dash_bootstrap_components as dbc

PUBLISH_BUTTONS = [
    "title",
    "si-block",
    "volumetric-map",
    "obj-files",
    "sci-images",
    "reports",
]


def confirm_update_modal(message, suffix):
    # add all publish buttons and only show the relevant one
    # this is necessary because we need unique id's to trigger the correct processing
    # activity, and a nonexistent id can't be an input on a callback.

    footer_contents = []
    visible_button = dbc.Button(
        "Publish",
        id=f"confirm-update-{suffix}",
        className="ms-auto",
        color="light",
        n_clicks=0,
        style={"display": "reset"},
    )
    for button in PUBLISH_BUTTONS:
        if button == suffix:
            pass
        else:
            footer_contents.append(
                dbc.Button(
                    "Publish",
                    id=f"confirm-update-{button}",
                    className="ms-auto",
                    color="light",
                    n_clicks=0,
                    style={"display": "none"},
                )
            )
    visible_contents = [
        dbc.Col(
            visible_button,
            width="auto",
        ),
        dbc.Col(
            dbc.Button(
                "Close",
                id="cancel-update",
                className="ms-auto",
                n_clicks=0,
            ),
            width="auto",
        ),
    ]
    footer_contents.extend(visible_contents)
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Publish Update")),
            dbc.ModalBody(message),
            dbc.ModalFooter([dbc.Row(footer_contents)]),
        ],
        id="confirm-update-modal",
        is_open=True,
    )


def failure_alert(message, className=None):
    return dbc.Alert(
        message,
        id="failure-alert",
        is_open=True,
        dismissable=True,
        fade=False,
        color="danger",
        className=className,
    )


def make_download(button_text, prefix):
    return [
        dbc.Button(
            button_text,
            id=f"{prefix}-example",
            color="primary",
        ),
        dcc.Download(id=f"{prefix}-example-dl"),
    ]


def make_upload(prefix, max_size, allow_multiple=False):
    return [
        dbc.Col(
            [
                dcc.Upload(
                    [
                        html.Div(
                            "Drag and Drop or Click to Select Files",
                        ),
                    ],
                    id=f"{prefix}-upload",
                    className="drop-zone",
                    max_size=max_size,
                    multiple=allow_multiple,
                ),
                html.Div(id=f"output-{prefix}-upload"),
            ]
        ),
        dbc.Col(
            dbc.Button("Publish", id=f"{prefix}-publish", color="warning"),
            width="auto",
        ),
    ]


def make_upload_card(
    header,
    dl_notes,
    prefix,
    max_size,
    dl_height=60,
    summary_note=None,
    example=True,
    accordion=False,
    acc_notes=None,
    upload_multiple=False,
):
    body_items = []
    if accordion:
        body_items.append(make_accordion(acc_notes))
    if summary_note:
        body_items.append(html.P(summary_note, className="card-summary-note"))
    for i in range(len(dl_notes)):
        row_contents = [
            dbc.Col(html.P(dl_notes[i])),
        ]
        if example:
            row_contents.append(
                dbc.Col(
                    make_download("Download example", f"{prefix}-{i}"),
                    width="auto",
                ),
            )
        if i == 0 and accordion:
            dl_row = dbc.Row(
                row_contents,
                align="center",
                style={"height": f"{dl_height}px", "margin-top": "15px"},
            )
        else:
            dl_row = dbc.Row(
                row_contents,
                align="center",
                style={"height": f"{dl_height}px"},
            )
        body_items.append(dl_row)
    if example and not accordion:
        body_items.append(html.Hr())
    if upload_multiple:
        body_items.append(
            dbc.Row(
                make_upload(prefix, max_size, allow_multiple=upload_multiple),
                align="center",
                class_name="upload-row",
            )
        )
    else:
        body_items.append(
            dbc.Row(
                make_upload(prefix, max_size), align="center", class_name="upload-row"
            )
        )
    return dbc.Card(
        [
            dbc.CardHeader(html.H4(header, className="upload-card-title")),
            dbc.CardBody(body_items),
        ],
        color="light",
        class_name="form-card",
    )


def make_accordion(items):
    accordion_items = []
    for item in items:
        this_item = dbc.AccordionItem(
            [item[1]],
            title=item[0],
        )
        accordion_items.append(this_item)
    return dbc.Accordion(accordion_items)
