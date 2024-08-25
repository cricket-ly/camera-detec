import json
import websockets

table_name = "test"
deploy_uri = "wss://cityio.media.mit.edu:443/cityio/interface"
wss_listen = "{\"type\":\"LISTEN\",\"content\":{\"gridId\":\"" + table_name + "\"}}"

# Track received data
data_store = {
    "A": None,
    "B": None,
    "C": None
}

def all_data_received():
    """Checks if all the data has been recevied before proceeding"""
    return all(data_store.values())

async def compiler(all_data):
    """Will compile the information and update the global grid"""
    # Assign the correct variables to their respective value
    mapped_data = all_data["A"]
    global_props = all_data["B"]
    global_ids_to_change = all_data["C"]

    for updated_info in mapped_data:
        # We need to update the json_str at each ID in list_ids_to_change by find the ID to change
        for item in global_props: #json_str is a LIST, each item is a DICT
            for global_id in global_ids_to_change:
                # Comparing the original ids -- item['id'] -- against the list of ids to change
                if item['id'] < global_id:
                    break # if we are at item['id'] of 0, and the first id_to_change is 2, 0 won't be in the list.

                elif item['id'] == global_id: # update it with the new information
                    item['color'] = updated_info['color']
                    item['height'] = updated_info['height']
                    item['interactive'] = updated_info['interactive']
                    item['name'] = updated_info['name']

    # Send the updated data
    print("Sending to table")
    print(mapped_data)
    await send_to_table(mapped_data)

async def send_to_table(global_mapped_data):
    """Updates the projection"""
    async with websockets.connect(deploy_uri, max_size=2**24, compression="deflate") as websocket:
        updated_grid = json.dumps({"type": "UPDATE_GRID", "content": {"geogriddata": global_mapped_data}}, separators=(',', ':'))
        print("Sending:", updated_grid)
        await websocket.send(updated_grid)

        # Optionally, await a response from the server to confirm the update was received
        response = await websocket.recv()
        print("Received:", response)


async def handle_client(client_id, message):
    """Checks if all of the information has been received before continuing to compile/process
    the data."""
    # Store the message for the corresponding client
    data_store[client_id] = message

    # Check if all clients have sent data
    if all_data_received():
        print("All data received. Processing...")
        # Now process the combined data from all clients
        combined_data = data_store.copy()  # Copy the data to process
        await compiler(combined_data)  # Now, actually compile the data together

        # Reset the data store after processing
        for key in data_store:
            data_store[key] = None
