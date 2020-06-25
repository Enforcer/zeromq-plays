import asyncio
import json

import zmq
import zmq.asyncio

ctx = zmq.asyncio.Context()

socket = ctx.socket(zmq.ROUTER)
socket.bind("ipc://ms.ipc")


orders = {"BUY": [], "SELL": []}


async def main():
    while True:
        data = await socket.recv_multipart()
        print('Got', data)
        identity = data[0]
        order = json.loads(data[1])

        other_side = "BUY" if order["side"] == "SELL" else "SELL"
        execution_report = {"status": None}
        if orders[other_side]:
            orders[other_side].pop()
            execution_report["status"] = "MATCHED"
        else:
            orders[order["side"]].append(order)
            execution_report["status"] = "NEW"

        #input('enter by kontynuowac')
        await socket.send_multipart([identity, json.dumps(execution_report).encode()])
        print('Orders now', orders)


try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    socket.close()
    ctx.term()

