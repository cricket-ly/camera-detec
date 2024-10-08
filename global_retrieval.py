import websockets
import asyncio
import json

table_name = "test"
deploy_uri = "wss://cityio.media.mit.edu:443/cityio/interface"
wss_listen = "{\"type\":\"LISTEN\",\"content\":{\"gridId\":\"" + table_name + "\"}}"

async def receive_data(deploy_uri, wss_listen):
    """This connects to the websocket server and collects data from it.
    What we need is number of ROWS, number of COLUMNS, and to make a copy
    of the current geogriddata information."""
    # Connect with the websocket, given by deploy_uri
    async with websockets.connect(deploy_uri, max_size=2**24, compression="deflate") as websocket:
        await websocket.send(wss_listen)
        # Creating default loading files:
        result_geo = await websocket.recv() #this is the whole json file of what is CURRENTLY on the table
        #print("Data received!")

        # Load the JSON file and go to the properties
        datajson = json.loads(result_geo)
        geogrid_properties = datajson['content']['GEOGRID']['properties']
        # print("geogrid_properties:", geogrid_properties)

        # Retrieve information on the rows and columns of the total grid
        total_rows = geogrid_properties['header']['nrows']
        total_columns = geogrid_properties['header']['ncols']
        # print("Total rows:",total_rows)
        # print("Total columns:",total_columns)

        # Load the properties of the /whole/ grid.
        # This is info on the color, height, name, interactive, and ID of each grid
        properties = [] # this is good because this is a copy, so we can edit this list
        for item in datajson['content']['GEOGRID']['features']: #each item is the properties of the aruco
             properties.append(item['properties'])
        # print("properties:",properties)
        # print("--------------")

        return(total_rows, total_columns, properties)


# Run the asynchronous function using asyncio.run
if __name__ == "__main__":
    total_rows, total_columns, original_properties = asyncio.run(receive_data())
    print("Rows:",total_rows,"Columns:",total_columns)
    print("Properties:",original_properties)
    #print(type(original_properties))
