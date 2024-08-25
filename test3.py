import websockets
from testcompile import handle_client
import numpy as np
import json
import asyncio

table_name = "test"
deploy_uri = "wss://cityio.media.mit.edu:443/cityio/interface"
wss_listen = "{\"type\":\"LISTEN\",\"content\":{\"gridId\":\"" + table_name + "\"}}"

async def function_c(initial, local_rows, local_columns):
    async with websockets.connect(deploy_uri, max_size=2**24, compression="deflate") as websocket:
        # Connect with the global grid and get the global rows and columns
        print("Awaiting")
        await websocket.send(wss_listen)
        print("received")

        global_grid = await websocket.recv()

        # Load the global JSON file
        datajson = json.loads(global_grid)
        geogrid_properties = datajson['content']['GEOGRID']['properties']
        global_rows = geogrid_properties['header']['nrows']
        global_columns = geogrid_properties['header']['ncols']
        # print("Total rows:",total_rows)
        # print("Total columns:",total_columns)

        # Determine the top right, bottom left, and bottom right of your smaller grid
        top_R = initial + (local_columns - 1)
        bottom_L = initial + (global_columns)*(local_rows-1)
        bottom_R = bottom_L + (local_columns - 1)

        # Create the two columns
        left_column = np.linspace(initial, bottom_L, local_rows)
        right_column = np.linspace(top_R, bottom_R, local_rows)

        # Create the matrix
        matrix = np.zeros((local_rows, local_columns, 2))

        # Generate the different indexes
        for i in range(local_rows):
            # Generate points interpolating between left_column[i] and right_column[i]
            x_values = np.linspace(left_column[i], right_column[i], local_columns)
            #print("x_values:",x_values)
            matrix[i, :, 0] = x_values  # Assign x-values to the first row

        # Only return the indexes
        x_coordinates = matrix[:, :, 0]

        flattened_array = x_coordinates.flatten()
        flattened_array = [int(x) for x in flattened_array]

        # Send the relevant information to handle_client()
        info = flattened_array
        #info = "Info from C"
        print("Yes, recevied from test3")
        await handle_client("C", info)

# if __name__ == "__main__":
#     asyncio.run(function_c(0, 3, 3))
