import time
import hashlib

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from skywalking.trace import tags
from skywalking.trace.tags import Tag
from skywalking.trace.carrier import Carrier
from skywalking.trace.context import Span, get_context
from skywalking import config, agent, Layer, Component


class FastAPISkywalkingMiddleware:
    def __init__(
            self,
            app: ASGIApp,
            *,
            service: str = "FastAPI",
            instance: str = None,
            collector: str = "127.0.0.1:11800",
            protocol_type: str = "grpc",
            token: str = None,
    ):
        self._app = app

        # initialize skywalking agent
        config.init(
            service=service,
            instance=instance,
            collector=collector,
            protocol_type=protocol_type,
            token=token,
        )
        agent.start()

    @staticmethod
    def _generate_trace_id():
        m = hashlib.md5()
        m.update(f"{time.time_ns()}".encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    async def _create_span(request: Request) -> Span:
        context = get_context()
        span = context.new_entry_span(op=request.url.path, carrier=Carrier())
        span.start()
        span.layer = Layer.Http
        span.component = Component.Requests
        span.peer = f"{request.client.host}:{request.client.port}"
        span.tag(tag=Tag(key=tags.HttpMethod, val=request.method, overridable=False))
        return span

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        # Create Request
        request = Request(scope, receive=receive)

        # After Request
        span = await self._create_span(request=request)
        scope.setdefault("trace_ctx", span)

        # Default status code used when the application does not return a valid response
        # or an unhandled exception occurs.
        status_code = 500

        async def wrapped_send(message: Message) -> None:
            if message['type'] == 'http.response.start':
                nonlocal status_code
                status_code = message['status']
            await send(message)

        try:
            await self._app(scope, receive, wrapped_send)
        except Exception as err:
            span.log(ex=err)
            span.raised()
        finally:
            if scope["type"] == "http":
                span.tag(Tag(key=tags.HttpUrl, val=str(request.url), overridable=False))
                span.tag(Tag(key=tags.HttpStatus, val=status_code, overridable=False))
                span.stop()
