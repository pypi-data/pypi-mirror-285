from trame_remote_control.widgets.remote_control import *  # noqa


def initialize(server):
    from trame_remote_control.modules import remote_control

    server.enable_module(remote_control)
