###############
# IMPORT FILES AND SET TABLE NAME
# Import the files
from global_retrieval import receive_data # used in global retrieval
from aruco_id_detector import * # used for initializing and for detecting
from update_global_with_local import *

# Determine the table to connect to
table_name = "test"
deploy_uri = "wss://cityio.media.mit.edu:443/cityio/interface"
wss_listen = "{\"type\":\"LISTEN\",\"content\":{\"gridId\":\"" + table_name + "\"}}"

###############
# GLOBAL RETRIEVAL
# Retrieve data from the GLOBAL grid. We want to know the global ROWS, COLS, and ORIGINAL PROPERTIES
class GlobalProperties:
    def __init__(self): # initializing
        self.total_rows = None
        self.total_columns = None
        self.properties = None

    async def retrieve(self):
        """Retrieve the total rows, total columns, and original properties asynchronously."""
        self.total_rows, self.total_columns, self.properties = await receive_data(deploy_uri, wss_listen)
        #print(f"Rows: {self.total_rows}\nColumns: {self.total_columns}\nProperties: {self.properties}")
        return self.total_rows, self.total_columns, self.properties

async def retrieve_global():
    """Retrieve data from the GLOBAL grid. Returns the global ROWS, COLS, and PROPERTIES"""
    # # GLOBAL RETRIEVAL
    global_props = GlobalProperties()

    # Retrieve the rows, columns, and properties
    rows, columns, properties = await global_props.retrieve()
    return rows, columns, properties

###############
# INITIALIZING THE GRID
# Figure out what portion of the GLOBAL grid we will be updating
# Return a list of integers which represent the GLOBAL indexes that will need to be updated
def create_smaller_grid(initial, local_rows, local_columns, global_cols):
    """Creates a smaller grid from the global grid (tracks the correct indexes)."""

    # Determine the top right, bottom left, and bottom right of your smaller grid
    top_R = initial + (local_columns - 1)
    bottom_L = initial + (global_cols)*(local_rows-1)
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

    return flattened_array
# Create the grid of coordinate points the camera will detect

###############
# DETECTION & MAPPING
# Detect the markers with the camera
# Map the ArUco markers detected to their properties ('color', 'height', 'id', 'interactive', and 'name')

###############
# UPDATING THE GLOBAL GRID
# We have the information of the markers in from the LOCAL grid. Now we need to update
# the GLOBAL grid to have this information

###############
# SENDING TO WEBSOCKET
# Send the updated GLOBAL grid

# async def send_to_websocket(json_data):
#     async with websockets.connect(deploy_uri, max_size=2**24, compression="deflate") as websocket:
#         await websocket.send(wss_listen)
#         ## MAPPING THE LOCAL MARKERS TO THEIR DATA
#         mapped_local_data = mapping_markers_to_data(json_data)
#         print(mapped_local_data)
#         input("Continue? ")

#         ## UPDATING RELEVANT PARTS OF THE GLOBAL GRID
#         def update_global(mapped_data, global_data, global_ids_to_change):
#             """Mapped data is the local information that needs to be updated to the global data."""
#             for updated_info in mapped_data:
#                 # We are looking at one specific cell now. We need to update the json_str at each ID in list_ids_to_change
#                 # So, we need to find the ID to change, in the original json_str
#                 for item in global_data: #json_str is a LIST, each item is a DICT
#                     for global_id in global_ids_to_change:
#                         # Comparing the original ids -- item['id'] -- against the list of ids to change
#                         if item['id'] < global_id:
#                             break # if we are at item['id'] of 0, and the first id_to_change is 2, 0 won't be in the list.
#                             # want to move onto the next item in the json_str

#                         elif item['id'] == global_id:
#                             #print("Original info:",item)
#                             # Now we want to update this info based on the information from mapping_markers
#                             #print("---------------")
#                             item['color'] = updated_info['color']
#                             item['height'] = updated_info['height']
#                             item['interactive'] = updated_info['interactive']
#                             item['name'] = updated_info['name']
#             return global_data

#         updated_global_data = update_global(json_data, global_properties, indexes_to_change)

#         ## SENDING THE INFORMATION TO THE TABLE
#         updated_grid = json.dumps({"type":"UPDATE_GRID","content":{"geogriddata":updated_global_data}},separators=(',', ':'))
#         print("SUCCESS")
#         await websocket.send(updated_grid)


###############
# Run the different parts of the program together
if __name__ == "__main__":
    ###############
    ## GLOBAL RETRIEVAL - done
    global_rows, global_cols, global_properties = asyncio.run(retrieve_global())
    print(f"Global data retrieved\nGlobal rows: {global_rows}\nGlobal columns: {global_cols}\nProperties: {global_properties}")
    input("Continue to initializing? ") # help with debugging
    print("-----------")

    ###############
    ## INITIALIZING THE GRID - done
    print("Initializing the local grid now.")
    initial = int(input("Top left corner of LOCAL grid: "))
    local_rows = int(input("Rows for LOCAL grid: "))
    local_cols = int(input("Columns for LOCAL grid: "))

    # Track the global indexes to update later in a LIST
    indexes_to_change = create_smaller_grid(initial, local_rows, local_cols, global_cols)
    print(indexes_to_change)
    input("Continue to calibrating grid? ") # help with debugging
    print("-----------")

    # Create the local grid and coordinates for the camera to detect
    desired_aruco_dictionary = "DICT_4X4_50"
    grid_position_dict = calibrate(desired_aruco_dictionary, local_rows, local_cols)
    print(grid_position_dict)
    input("Continue to detecting?? ") # help with debugging
    print("-----------")

    ###############
    ## DETECTION & MAPPING

    asyncio.run(main_detection(grid_position_dict))
    # Detect the local markers - needs the coordinate of points to look for. Returns the JSON

    # Map the markers - needs the data_file of markers to map. RETURNS a LIST w/ color, height, etc

    # Update the global grid - needs the local data, original grid data, list of IDs. RETURNS  a LIST

    # Send this information to the websocket

# Show the frames
