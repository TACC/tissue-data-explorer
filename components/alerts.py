import dash_bootstrap_components as dbc


def send_toast(header: str, message: str, type: str):
    if type == "success":
        return (
            dbc.Toast(
                message,
                id="toast-msg",
                header=header,
                is_open=True,
                dismissable=True,
                class_name="result-toast",
                header_class_name="text-success",
                duration=4000,
            ),
        )
    else:
        return (
            dbc.Toast(
                message,
                id="toast-msg",
                header=header,
                is_open=True,
                dismissable=True,
                class_name="result-toast",
                header_class_name="text-danger",
                duration=4000,
            ),
        )
