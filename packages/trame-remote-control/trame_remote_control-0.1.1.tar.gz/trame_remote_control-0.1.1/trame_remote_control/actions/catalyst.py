import logging
from trame.widgets import html, vuetify
from paraview import simple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global Reference to the Catalyst Connection
_catalyst_connection = None


def open_catalyst(state, ctrl, body: dict):
    """
    Called when the app should open a Catalyst connection. Does not need any parameters.
    """
    global _catalyst_connection
    logger.info(f"Opening Catalyst connection")

    _catalyst_connection = simple.servermanager.ConnectToCatalyst()
    state.catalyst_open = True


# All POST Request must have an "action" field, which specified what to execute
ACTIONS = {
    "open_catalyst": open_catalyst,
}


def create_panel(server):
    """
    Create the Panel for manually opening and closing a Catalyst connection.
    """
    state, ctrl = server.state, server.controller

    # Catalyst closed by default
    state.catalyst_open = False

    def _open():
        open_catalyst(state, ctrl, {})

    with vuetify.VCard(classes="pa-0", flat=True, outlined=False, tile=True):
        vuetify.VDivider()
        with vuetify.VCardTitle(classes="d-flex align-center py-1"):
            html.Div("ParaView Catalyst")

        vuetify.VDivider()

        # Catalyst closed
        with vuetify.VCardText(v_if=("!catalyst_open",)):
            html.Div(f"Catalyst Connection not open")
            vuetify.VBtn("Connect", block=True, small=True, color="success", click=_open)

        # Catalyst open
        with vuetify.VCardText(v_if=("catalyst_open",)):
            html.Div(f"Catalyst Connection available")
