import logging

from pv_visualizer.app.engine import ParaviewProxyManager

from trame.widgets import html, vuetify
from paraview import simple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def connect(state, ctrl, body: dict):
    """
    Called when the app should connect to a ParaView Server.

    Required Parameters in body:
        - url (string): URL where the server is listening
        - port (integer, optional): Port where the server is listening. Defaults to 11111.
    """
    url = body["url"]
    port = int(body.get("port", 11111))
    logger.info(f"Connecting to ParaVeiw Server at '{url}:{port}'")

    simple.Connect(url, port)

    # Set State for UI
    state.server_connection = f"{url}:{port}"


def disconnect(state, ctrl, body: dict):
    """
    Called when the app should disconnect to a ParaView Server. Does not need any parameters.
    """
    logger.info(f"Disconnecting from ParaVeiw Server")

    simple.Disconnect()
    state.server_connection = None


# All POST Request must have an "action" field, which specified what to execute.
ACTIONS = {
    "connect": connect,
    "disconnect": disconnect,
}


def create_panel(server):
    """
    Create the Panel for manually connecting and disconnecting the a ParaVeiw Server.
    """
    state, ctrl = server.state, server.controller

    # No ParaView Connection by default
    state.server_connection = None

    def _connect():
        connect(state, ctrl, {
            "url": state.server_connection_url,
            "port": state.server_connection_port,
        })

    def _disconnect():
        disconnect(state, ctrl, {})

    with vuetify.VCard(classes="pa-0", flat=True, outlined=False, tile=True):
        vuetify.VDivider()
        with vuetify.VCardTitle(classes="d-flex align-center py-1"):
            html.Div("ParaView Server Connection")

        vuetify.VDivider()

        # Connection exists
        with vuetify.VCardText(v_if=("server_connection",)):
            html.Div(f"Connected to Server on '{state.server_connection}'")
            vuetify.VBtn("Disconnect", block=True, small=True, color="success", click=_disconnect)

        # Connection doesn't exist
        with vuetify.VCardText(v_if=("!server_connection",)):
            html.Div(f"Not connected to a ParaView Server")

            with vuetify.VForm(submit=_connect):
                vuetify.VTextField(v_model=("server_connection_url", "localhost"), label="URL")
                vuetify.VTextField(v_model=("server_connection_port", "11111"), label="Port", type="number")
                vuetify.VBtn("Connect", type="submit", block=True, small=True, color="success")
