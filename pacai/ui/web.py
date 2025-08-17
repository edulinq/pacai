import base64
import errno
import http
import http.server
import io
import logging
import mimetypes
import os
import re
import socket
import threading
import time
import typing
import urllib.parse
import webbrowser

import PIL.Image
import edq.util.dirent
import edq.util.json

import pacai.core.action
import pacai.core.board
import pacai.core.gamestate
import pacai.core.ui

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
STATIC_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'webui')

START_PORT: int = 30000
END_PORT: int = 40000

INITIAL_SLEEP_TIME_SEC: float = 0.05
SOCKET_SLEEP_TIME_SECS: float = 0.10
SERVER_WAIT_TIME_SECS: float = 0.25
REAP_TIME_SECS: float = 0.25
COMPLETE_WAIT_TIME_SECS: float = 0.15

SERVER_POLL_INTERVAL_SECS: float = 0.1

RequestHandlerResult: typing.TypeAlias = tuple[dict | str | bytes | None, int | None, dict | None] | None

class WebUserInputDevice(pacai.core.ui.UserInputDevice):
    """
    A user input device that gets input from the same web page used by a WebUI.
    """

    def __init__(self,
            char_mapping: dict[str, pacai.core.action.Action] | None = None,
            **kwargs: typing.Any) -> None:
        self._actions: list[pacai.core.action.Action] = []
        """ The actions stored from the web page. """

        self._lock: threading.Lock = threading.Lock()
        """ A lock to protect the user actions. """

        if (char_mapping is None):
            char_mapping = pacai.core.ui.DUAL_CHAR_MAPPING

        self._char_mapping: dict[str, pacai.core.action.Action] = char_mapping
        """ Map characters to actions. """

    def add_keys(self, keys: list[str]) -> None:
        """ Load key inputs from the UI into this device. """

        actions = []
        for key in keys:
            if (key in self._char_mapping):
                actions.append(self._char_mapping[key])

        with self._lock:
            self._actions += actions

    def get_inputs(self) -> list[pacai.core.action.Action]:
        with self._lock:
            actions = self._actions
            self._actions = []
            return actions

class HTTPHandler(http.server.BaseHTTPRequestHandler):
    """ Handle HTTP requests for the web UI. """

    _lock: threading.Lock = threading.Lock()
    """ A lock to protect the data sent to the web page. """

    _user_input_device: WebUserInputDevice | None = None
    """ Put all user input into this device. """

    _fps: int | None = None
    """ The FPS the web UI should run at. """

    _state: pacai.core.gamestate.GameState | None = None
    """ The current game state. """

    _image_url: str | None = None
    """ The data URL for the current image. """

    @classmethod
    def ui_setup(cls, fps: int, user_input_device: WebUserInputDevice) -> None:
        """ Initialize this handler with information from the UI. """

        cls._fps = fps
        cls._user_input_device = user_input_device

    @classmethod
    def set_data(cls, state: pacai.core.gamestate.GameState, image: PIL.Image.Image) -> None:
        """ Set the data passed back to the web page. """

        buffer = io.BytesIO()
        image.save(buffer, format = 'png')
        data_64 = base64.b64encode(buffer.getvalue()).decode(edq.util.dirent.DEFAULT_ENCODING)
        data_url = f"data:image/png;base64,{data_64}"

        with cls._lock:
            cls._state = state.copy()
            cls._image_url = data_url

    @classmethod
    def get_data(cls) -> tuple[pacai.core.gamestate.GameState | None, str | None]:
        """ Get the data passed back to the web page. """

        with cls._lock:
            return cls._state, cls._image_url

    def log_message(self, *args: typing.Any) -> None:
        """
        Reduce the logging noise.
        """

    def handle(self) -> None:
        """
        Override handle() to ignore dropped connections.
        """

        try:
            http.server.BaseHTTPRequestHandler.handle(self)
        except BrokenPipeError:
            logging.info("Connection closed on the client side.")

    def do_POST(self) -> None:  # pylint: disable=invalid-name
        """ Handle POST requests. """

        self._handle_request(self._get_post_data)

    def do_GET(self) -> None:  # pylint: disable=invalid-name
        """ Handle GET requests. """

        self._handle_request(self._get_get_data)

    def _handle_request(self, data_handler: typing.Callable) -> None:
        logging.trace("Serving: '%s'.", self.path)  # type: ignore[attr-defined]  # pylint: disable=no-member

        code: int = http.HTTPStatus.OK
        headers: dict[str, typing.Any] = {}

        result = None
        try:
            data = data_handler()
            result = self._route(self.path, data)
        except Exception as ex:
            # An error occured during data handling (routing captures their own errors).
            logging.debug("Error handling '%s'.", self.path, exc_info = ex)
            result = (str(ex), http.HTTPStatus.BAD_REQUEST, None)

        if (result is None):
            # All handling was done internally, the response is complete.
            return

        # A standard response structure was returned, continue processing.
        payload, response_code, response_headers = result

        if (isinstance(payload, dict)):
            payload = edq.util.json.dumps(payload)
            headers['Content-Type'] = 'application/json'

        if (isinstance(payload, str)):
            payload = payload.encode(edq.util.dirent.DEFAULT_ENCODING)

        if (payload is not None):
            headers['Content-Length'] = len(payload)

        if (response_headers is not None):
            for key, value in response_headers.items():
                headers[key] = value

        if (response_code is not None):
            code = response_code

        self.send_response(code)

        for (key, value) in headers.items():
            self.send_header(key, value)
        self.end_headers()

        if (payload is not None):
            self.wfile.write(payload)

    def _route(self, path: str, params: dict[str, typing.Any]) -> RequestHandlerResult:
        path = path.strip()

        target = _handler_not_found
        for (regex, handler_func) in ROUTES:
            if (re.search(regex, path) is not None):
                target = handler_func
                break

        try:
            return target(self, path, params)
        except Exception as ex:
            logging.error("Error on path '%s', handler '%s'.", path, str(target), exc_info = ex)
            return str(ex), http.HTTPStatus.INTERNAL_SERVER_ERROR, None

    def _get_get_data(self) -> dict[str, typing.Any]:
        path = self.path.strip().rstrip('/')
        url = urllib.parse.urlparse(path)

        raw_params = urllib.parse.parse_qs(url.query)
        params: dict[str, typing.Any] = {}

        for (key, values) in raw_params.items():
            if ((len(values) == 0) or (values[0] == '')):
                continue

            if (len(values) == 1):
                params[key] = values[0]
            else:
                params[key] = values

        return params

    def _get_post_data(self) -> dict[str, typing.Any]:
        length = int(self.headers['Content-Length'])
        payload = self.rfile.read(length).decode(edq.util.dirent.DEFAULT_ENCODING)

        try:
            request = edq.util.json.loads(payload)
        except Exception as ex:
            raise ValueError("Payload is not valid json.") from ex

        return request  # type: ignore[no-any-return]

class WebUI(pacai.core.ui.UI):
    """
    A UI that starts a web server and launches a brower window to serve a UI.
    The web server will accept requests that contains user inputs,
    and respond with the current game state and a visual representation of the game (a base64 encoded png).
    """

    def __init__(self,
            **kwargs: typing.Any) -> None:
        input_device = WebUserInputDevice(**kwargs)
        super().__init__(user_input_device = input_device, **kwargs)

        self._port: int = -1
        """
        The port to start the web server on.
        The first open port in [START_PORT, END_PORT] will be used.
        """

        self._startup_barrier: threading.Barrier = threading.Barrier(2)
        """ Use a threading barrier to wait for the server thread to start. """

        self._server_thread: threading.Thread | None = None
        """ The thread the server will be run on. """

        self._server: http.server.HTTPServer | None = None
        """ The HTTP server. """

    def game_start(self,
            initial_state: pacai.core.gamestate.GameState,
            board_highlights: list[pacai.core.board.Highlight] | None = None,
            **kwargs: typing.Any) -> None:
        self._start_server()

        super().game_start(initial_state, board_highlights = board_highlights)

        self._launch_page(initial_state)

    def game_complete(self,
            final_state: pacai.core.gamestate.GameState,
            board_highlights: list[pacai.core.board.Highlight] | None = None,
            ) -> None:
        super().game_complete(final_state, board_highlights = board_highlights)

        # Wait for the UI to make a final request.
        time.sleep(COMPLETE_WAIT_TIME_SECS)

        self._stop_server()

    def draw(self, state: pacai.core.gamestate.GameState, **kwargs: typing.Any) -> None:
        image = self.draw_image(state)
        HTTPHandler.set_data(state, image)

    def _start_server(self) -> None:
        """ Start the HTTP server on another thread. """

        # Fetch the port.
        self._port = _find_open_port()

        # Setup the barrier to wait for the server thread to start.
        self._startup_barrier.reset()

        # Create, but don't start the server.
        self._server = http.server.ThreadingHTTPServer(('', self._port), HTTPHandler)

        # Setup the handler.
        HTTPHandler.ui_setup(self._fps, typing.cast(WebUserInputDevice, self._user_input_device))

        self._server_thread = threading.Thread(target = _run_server, args = (self._server, self._startup_barrier))
        self._server_thread.start()

        # Wait for the server to startup.
        self._startup_barrier.wait()
        time.sleep(INITIAL_SLEEP_TIME_SEC)

    def _stop_server(self) -> None:
        """ Stop the HTTP server and thread. """

        if ((self._server is None) or (self._server_thread is None)):
            return

        self._server.shutdown()
        time.sleep(SERVER_WAIT_TIME_SECS)

        if (self._server_thread.is_alive()):
            self._server_thread.join(REAP_TIME_SECS)

        self._server = None
        self._server_thread = None

    def _launch_page(self, initial_state: pacai.core.gamestate.GameState) -> None:
        """ Open the browser window to the web UI page. """

        image = self.draw_image(initial_state)
        HTTPHandler.set_data(initial_state, image)

        logging.info("Starting web UI on port %d.", self._port)
        logging.info("If a browser window does not open, you may use the following link:")
        logging.info("http://127.0.0.1:%d", self._port)

        webbrowser.open(f"http://127.0.0.1:{self._port}/static/index.html")

def _find_open_port() -> int:
    """ Go through [START_PORT, END_PORT] looking for open ports. """

    for port in range(START_PORT, END_PORT + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', port))

            # Explicitly close the port and wait a short amount of time for the port to clear.
            # This should not be required because of the socket option above,
            # but the cost is small.
            sock.close()
            time.sleep(SOCKET_SLEEP_TIME_SECS)

            return port
        except socket.error as ex:
            sock.close()

            if (ex.errno == errno.EADDRINUSE):
                continue

            # Unknown error.
            raise ex

    raise ValueError(f"Could not find open port in [{START_PORT}, {END_PORT}].")

def _run_server(server: http.server.HTTPServer, startup_barrier: threading.Barrier) -> None:
    """ Run the http server on this curent thread. """

    startup_barrier.wait()
    server.serve_forever(poll_interval = SERVER_POLL_INTERVAL_SECS)
    server.server_close()

@typing.runtime_checkable
class RequestHandler(typing.Protocol):
    """ Functions that can be used as HTTP request handlers by HTTPHandler. """

    def __call__(self, handler: HTTPHandler, path: str, params: dict) -> RequestHandlerResult:
        ...

def _handler_not_found(handler: HTTPHandler, path: str, params: dict) -> RequestHandlerResult:
    """ Handle a 404. """

    return (f"404 route not found: '{path}'.", http.HTTPStatus.NOT_FOUND, None)

def _handler_redirect(target: str) -> RequestHandler:
    """ Get a handler that redirects to the specific target. """

    def handler_func(handler: HTTPHandler, path: str, params: dict) -> RequestHandlerResult:
        return (None, http.HTTPStatus.MOVED_PERMANENTLY, {'Location': target})

    return handler_func

def _handler_static(handler: HTTPHandler, path: str, params: dict) -> RequestHandlerResult:
    """ Get a static (bundled) file. """

    # Note that the path is currently a URL path, and therefore separated with slashes.
    parts = path.strip().lstrip('/').split('/')

    # Remove the static prefix.
    if (parts[0] == 'static'):
        parts.pop(0)

    static_path = os.path.join(STATIC_DIR, *parts)
    logging.trace("Serving static path: '%s'.", static_path)  # type: ignore[attr-defined]  # pylint: disable=no-member

    if (not os.path.isfile(static_path)):
        return (f"404 static path not found '{path}'.", http.HTTPStatus.NOT_FOUND, None)

    data = edq.util.dirent.read_file_bytes(static_path)

    code = http.HTTPStatus.OK
    headers = {}

    mime_info = mimetypes.guess_type(path)
    if (mime_info is not None):
        headers['Content-Type'] = mime_info[0]

    return data, code, headers

def _handler_init(handler: HTTPHandler, path: str, params: dict) -> RequestHandlerResult:
    """ Handle a request by the browser to initialize. """

    data = {
        'title': 'pacai',
        'fps': handler._fps,
    }

    return (data, None, None)

def _handler_update(handler: HTTPHandler, path: str, params: dict) -> RequestHandlerResult:
    """ Handle a request by the browser for more data. """

    state, image_url = handler.get_data()
    data = {
        'state': state,
        'image_url': image_url,
    }

    keys = params.get('keys', [])
    if (handler._user_input_device is not None):
        handler._user_input_device.add_keys(keys)

    return (data, None, None)

ROUTES: list[tuple[str, RequestHandler]] = [
    (r'^/$', _handler_redirect('/static/index.html')),
    (r'^/index.html$', _handler_redirect('/static/index.html')),
    (r'^/static$', _handler_redirect('/static/index.html')),
    (r'^/static/$', _handler_redirect('/static/index.html')),

    (r'^/favicon.ico$', _handler_redirect('/static/favicon.ico')),

    (r'^/static/', _handler_static),

    (r'^/api/init$', _handler_init),
    (r'^/api/update$', _handler_update),
]
