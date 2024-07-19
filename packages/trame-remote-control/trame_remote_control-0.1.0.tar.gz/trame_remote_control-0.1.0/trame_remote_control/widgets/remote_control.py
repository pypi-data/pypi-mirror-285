from trame.widgets import vuetify
from trame_remote_control.actions import paraview_server, catalyst

NAME = "juviz-controller"
ICON = "mdi-eye-settings"
ICON_STYLE = {}

COMPACT = {
    "dense": True,
    "hide_details": True,
}


def create_panel(server):
    with vuetify.VCol(v_if=(f"active_controls == '{NAME}'",), classes="mx-0 pa-0", **COMPACT):
        paraview_server.create_panel(server)
        catalyst.create_panel(server)
