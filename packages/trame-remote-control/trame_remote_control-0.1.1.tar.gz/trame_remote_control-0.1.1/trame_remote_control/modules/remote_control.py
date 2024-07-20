import logging
import os
from aiohttp import web

from trame_remote_control.actions import paraview_server, catalyst

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_actions = {
    **paraview_server.ACTIONS,
    **catalyst.ACTIONS
}


def setup(server):
    state, ctrl = server.state, server.controller

    async def handle_post(request: web.Request) -> web.StreamResponse:
        assert request.content_type == 'application/json', "POST request have be JSON Content"

        body: dict = await request.json()
        logger.debug(f"Received POST request: {body}")

        try:
            action_name = body["action"].lower()
            logger.info(f"Executing action: {action_name!r}")

            _actions[action_name](state, ctrl, body)
        except KeyError:
            return web.HTTPBadRequest(reason=f"Invalid action")

        return web.HTTPOk()

    api_endpoint = os.environ.get("REMOTE_CONTROL_ENDPOINT", "/api")
    if not api_endpoint.startswith("/"):
        api_endpoint = "/" + api_endpoint

    @ctrl.add("on_server_bind")
    def add_routes(wslink_server):
        wslink_server.app.add_routes(
            [web.post(api_endpoint, handle_post)]
        )

        logger.info(f"Initialized remote-control endpoint at {api_endpoint!r}")
