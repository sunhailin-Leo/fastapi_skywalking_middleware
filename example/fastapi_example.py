import asyncio

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from skywalking.decorators import trace
from skywalking.trace.context import Span
from skywalking.trace.tags import Tag
from starlette.requests import Request

from fastapi_skywalking_middleware.middleware import FastAPISkywalkingMiddleware

# Init server context
app = FastAPI()
app.add_middleware(
    FastAPISkywalkingMiddleware,
    service_name="your-service-name",
    service_instance="your-service-instance",
    collector_address="10.30.8.116:30799",
    protocol="grpc",
    authentication="your-authentication",
)


class RequestItem(BaseModel):
    waybill_id: str = ""


@trace()
async def inner_function_3():
    await asyncio.sleep(0.1)


@trace()
async def inner_function_2():
    await asyncio.sleep(0.2)


@trace()
async def inner_function():
    # Function
    await asyncio.sleep(0.05)
    await inner_function_2()


@app.post("/testPost")
async def api_post_test(item: RequestItem, request: Request):
    # If request header is application/json,
    # so you can set the request data to Skywalking Trace Tag
    ctx: Span = request.scope.get("trace_ctx")

    class BodyTag(Tag):
        key = "request.body"
        overridable = False

    ctx.tag(tag=BodyTag(val=item.json()))

    # Test Function 1, Function 2 is inside the Function 1
    await inner_function()

    await asyncio.sleep(0.1)

    # Test Function 3
    await inner_function_3()
    return "ok"


if __name__ == '__main__':
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8080,
        workers=1,
        reload=False,
        debug=False,
    )
