import uuid
import random

import fastapi
import zmq
import zmq.asyncio

ctx = zmq.asyncio.Context()

app = fastapi.FastAPI()


order_ids = iter(range(10000))

@app.get("/status")
def status():
    return {"status": "ok"}

@app.get("/orders")
async def post_order():
    order = {"id": next(order_ids), "side": random.choice(["BUY", "SELL"])}

    report = await send_order_and_get_execution_report(order)

    return report


async def send_order_and_get_execution_report(order):
    socket = ctx.socket(zmq.DEALER)
    try:
        socket.setsockopt(zmq.IDENTITY, str(uuid.uuid4()).encode())
        socket.connect("ipc://ms.ipc")

        await socket.send_json(order)
        return await socket.recv_json()
    finally:
    	socket.close()
