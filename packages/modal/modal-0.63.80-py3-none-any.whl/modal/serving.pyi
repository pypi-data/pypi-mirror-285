import modal.client
import modal.runner
import multiprocessing.context
import multiprocessing.synchronize
import synchronicity.combined_types
import typing
import typing_extensions

_App = typing.TypeVar("_App")

def _run_serve(
    app_ref: str, existing_app_id: str, is_ready: multiprocessing.synchronize.Event, environment_name: str
): ...
async def _restart_serve(
    app_ref: str, existing_app_id: str, environment_name: str, timeout: float = 5.0
) -> multiprocessing.context.SpawnProcess: ...
async def _terminate(proc: typing.Union[multiprocessing.context.SpawnProcess, None], timeout: float = 5.0): ...
async def _run_watch_loop(
    app_ref: str, app_id: str, watcher: typing.AsyncGenerator[typing.Set[str], None], environment_name: str
): ...
def _get_clean_app_description(app_ref: str) -> str: ...
def _serve_app(
    app: _App,
    app_ref: str,
    _watcher: typing.Union[typing.AsyncGenerator[typing.Set[str], None], None] = None,
    environment_name: typing.Union[str, None] = None,
) -> typing.AsyncContextManager[_App]: ...
def _serve_stub(
    app: modal.runner._App,
    *,
    client: typing.Union[modal.client._Client, None] = None,
    detach: bool = False,
    environment_name: typing.Union[str, None] = None,
    interactive: bool = False,
): ...

class __serve_app_spec(typing_extensions.Protocol):
    def __call__(
        self,
        app: _App,
        app_ref: str,
        _watcher: typing.Union[typing.Generator[typing.Set[str], None, None], None] = None,
        environment_name: typing.Union[str, None] = None,
    ) -> synchronicity.combined_types.AsyncAndBlockingContextManager[_App]: ...
    def aio(
        self,
        app: _App,
        app_ref: str,
        _watcher: typing.Union[typing.AsyncGenerator[typing.Set[str], None], None] = None,
        environment_name: typing.Union[str, None] = None,
    ) -> typing.AsyncContextManager[_App]: ...

serve_app: __serve_app_spec

def serve_stub(*args, **kwargs): ...
