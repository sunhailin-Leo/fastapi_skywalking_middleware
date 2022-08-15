import asyncio
import time
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from fastapi_skywalking_middleware.middleware import FastAPISkywalkingMiddleware


@pytest.fixture(name="test_middleware")
def test_middleware():

    def _test_middleware(**profiler_kwargs):
        app = FastAPI()
        app.add_middleware(FastAPISkywalkingMiddleware, **profiler_kwargs)

        @app.route("/test")
        async def normal_request(request):
            await asyncio.sleep(0.5)
            return JSONResponse({"retMsg": "Normal Request test Success!"})

        return app
    return _test_middleware


class TestProfilerMiddleware:
    @pytest.fixture
    def client(self, test_middleware):
        return TestClient(test_middleware())

    def test_skywalking(self, client):
        # request
        request_path = "/test"
        client.get(request_path)
