# trame-remote-control
A trame extension to allow outside programs to send instructions to a trame app.

*trame-remote-control* attaches a REST-API endpoint, which can be used by outside programs to send instrctions, 
called **actions** to the program. This can, e.g., be used to initialite a Connection between a trame app and a ParaView Server.

## Supported Actions
The API endpoint will by default initialized on the `/api` path, which can be changed be setting the `REMOTE_CONTROL_ENDPOINT` 
environment variable to a different location.

To trigger an action, send a POST request to the API path. The body must contain a JSON, which specifies the action to trigger 
and might contain the parameters for that action. See the list below for the supported actions and their required parameters:

```json
{
  "action": "connect",
  "url": "localhost",
  "port": 11111
}
```

| Action Name     | Parameters                              | Description                                                           |
|-----------------|-----------------------------------------|-----------------------------------------------------------------------|
| `connect`       | url: string, port: optional int = 11111 | Connect a trame-vtk app to a ParaView Serverrunning on `<url>:<port>` |
| `diconnect`     |                                         | Disconnect from a previously connected ParaView Server                |
| `open_catalyst` |                                         | Open a Catalyst connection                                            |

## Installing
To install this extension, execute `pip install trame-remote-control`

For a Development install, clone the repository and execute `pip install -e .`


## Usage
After you installed the extension, import the module via trame.
To initialize the API endpoint, execute the `initialize` method. 
If you, optionally, want to create the UI Elements to trigger action from within the application, you can execute `create_panel`:

```python
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, remote_control

def main():
    server = get_server()
    
    ... # Other initialization
    
    remote_control.initialize(server)

    # Create UI
    with SinglePageLayout(server):
        ...

        with vuetify.VCol():
            remote_control.create_panel(server)
```

## ToDos
- Allow developers to specify which Actions are initialized
- Add ping route to retrieve if application has finished loading and which Actions are available
- Create more Actions
