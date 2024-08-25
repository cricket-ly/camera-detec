import websockets
from testcompile import handle_client
import json
import asyncio

table_name = "test"
deploy_uri = "wss://cityio.media.mit.edu:443/cityio/interface"
wss_listen = "{\"type\":\"LISTEN\",\"content\":{\"gridId\":\"" + table_name + "\"}}"

async def function_b():
    async with websockets.connect(deploy_uri, max_size=2**24, compression="deflate") as websocket:
        await websocket.send(wss_listen)
        # Receive the global grid information
        global_grid = await websocket.recv()

        # Load the global JSON file
        datajson = json.loads(global_grid)

        # Load the properties. This is info on the color, height, name, interactive, and ID of each grid
        properties = []
        for item in datajson['content']['GEOGRID']['features']:
             properties.append(item['properties'])

        # Send the properties to the handle(client)
        info = properties
        print("Yes, recevied from test2")
        await handle_client("B", info)

# if __name__ == "__main__":
#     asyncio.run(function_b())
