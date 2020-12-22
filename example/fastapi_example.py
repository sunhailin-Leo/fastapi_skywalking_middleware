import time

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request

from skywalking.trace.tags import Tag
from skywalking.decorators import trace
from skywalking.trace.context import Span

from fastapi_skywalking_middleware.middleware import FastAPISkywalkingMiddleware

# Init server context
app = FastAPI()
app.add_middleware(FastAPISkywalkingMiddleware, collector="10.30.8.116:30799")


class RequestItem(BaseModel):
    waybill_id: str = ""


@trace()
async def inner_function_3():
    time.sleep(0.1)


@trace()
async def inner_function_2():
    time.sleep(0.2)


@trace()
async def inner_function():
    # Function
    time.sleep(0.05)
    await inner_function_2()


@app.post("/testPost")
async def api_post_test(item: RequestItem, request: Request):
    # If request header is application/json,
    # so you can set the request data to Skywalking Trace Tag
    ctx: Span = request.scope.get("trace_ctx")
    ctx.tag(tag=Tag(key="request.body", val=item.json(), overridable=False))

    # Test Function 1, Function 2 is inside the Function 1
    await inner_function()

    time.sleep(0.1)

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
