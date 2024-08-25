import websockets
from mapping_markers import mapping_markers_to_data
import json
from update_global_with_local import *
from side_functions import *

table_name = "test"
deploy_uri = "wss://cityio.media.mit.edu:443/cityio/interface"
wss_listen = "{\"type\":\"LISTEN\",\"content\":{\"gridId\":\"" + table_name + "\"}}"

# Choose a specific dictionary of ArUco markers and the camera index
desired_aruco_dictionary = "DICT_4X4_50"
camera = 0

# The different ArUco dictionaries built into the OpenCV library.
ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL
}

this_aruco_dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT[desired_aruco_dictionary])
this_aruco_parameters = cv2.aruco.DetectorParameters()

def calibrate(desired_aruco_dictionary, rows, columns):
    """Calibrates the camera and determines the matrix grid size of ArUco markers to detect.

    Parameter is a STRING which is the name of the desired ArUco dictionary.

    Returns a DICT with the center positions of each point in the matrix grid.
    """
    # Start the video stream
    cap = cv2.VideoCapture(camera)

    # Create a function that will check if there is a valid amount of markers
    def valid_amount():
        # Detect the corner markers
        detected = get_coordinates(desired_aruco_dictionary)

        # Check if amount detected == 4
        if len(detected) != 4:
            print(f"Detected {len(detected)} markers. Re-try and place 4 markers.")
            detected = valid_amount()

        return detected
    detected = valid_amount()

    # Isolate the corner coordinates and sort them
    def sorting(detected):
        corners = []
        for elem in detected: # elem is (Marker ID,  (x, y) )
            corners.append(elem[1])
        corners = sorted(corners)   # [(x0,y0), (x1,y1), (x2,y2), (x3,x3)]
        """NOTE: This is an issue when we have warping. This is not always true
        """
        return corners
    corners = sorting(detected)

    # Check that the markers are in a rectangle-ish shape
    def check_alignment(corners):
        """Checks if the corners are in a rectangle.

        Returns top_L, top_R, bottom_L, and bottom_R."""
        # First two in list should be leftmost, last two in list should be rightmost
        leftA, leftB = ( corners[0], corners[1] )
        rightA, rightB = ( corners[2], corners[3] )

        # Determine which ones are the top left, top right, bottom left, and bottom right
        if leftA[1] < leftB[1]:
            top_L = leftA
            bottom_L = leftB
        else:
            top_L = leftB
            bottom_L = leftA

        if rightA[1] < rightB[1]:
            top_R = rightA
            bottom_R = rightB
        else:
            top_R = rightB
            bottom_R = rightA

        # Check the x's are aligned
        if not bottom_L[0] - leeway < top_L[0] < bottom_L[0] + leeway:
            print("[1] Matrix is not in rectangle shape. Fix position of camera or markers.")
            detected = valid_amount()
            corners = sorting(detected)
            (top_L, top_R, bottom_L, bottom_R) = check_alignment(corners)

        if not top_R[0] - leeway < bottom_R[0] < top_R[0] + leeway:
            print("[2] Matrix is not in rectangle shape. Fix position of camera or markers.")
            detected = valid_amount()
            corners = sorting(detected)
            (top_L, top_R, bottom_L, bottom_R) = check_alignment(corners)

        # Check the y's are aligned
        if not top_R[1] - leeway < top_L[1] < top_R[1] + leeway:
            print("[3] Matrix is not in rectangle shape. Fix position of camera or markers.")
            detected = valid_amount()
            corners = sorting(detected)
            (top_L, top_R, bottom_L, bottom_R) = check_alignment(corners)

        if not bottom_L[1] - leeway < bottom_R[1] < bottom_L[1] + leeway:
            print("[4] Matrix is not in rectangle shape. Fix position of camera or markers.")
            detected = valid_amount()
            corners = sorting(detected)
            (top_L, top_R, bottom_L, bottom_R) = check_alignment(corners)

        return (top_L, top_R, bottom_L, bottom_R)
    leeway = 20
    (top_L, top_R, bottom_L, bottom_R) = check_alignment(corners)

    # Create matrix using these four corner points, generating the other center points
    matrix = generate_matrix(top_L, top_R, bottom_L, bottom_R, rows, columns)
    grid_dict = matrix_to_dict(matrix, rows, columns)
    print("Camera successfully calibrated.")

    # DEBUGGING CODE
    #print(grid_dict)
    return grid_dict

async def map_for_websocket(json_data):
    async with websockets.connect(deploy_uri, max_size=2**24, compression="deflate") as websocket:
        await websocket.send(wss_listen)
        # Map markers to their correct data
        json_str = mapping_markers_to_data(json_data)
        print("JSON str:",json_str)



#######################################

        # Change the table
        updated_grid = json.dumps({"type":"UPDATE_GRID","content":{"geogriddata":json_str}},separators=(',', ':'))
        await websocket.send(updated_grid)
        #print("Updated grid:",updated_grid)
        print("-------------------")

        ###################
        # This is just to test if the data is really sent to the websocket or not
        # file_path = 'mapped_data/mapped_file_0.json'

        # with open(file_path, 'r') as file:
        #     json_data = json.load(file)

        # Change the volpe table
        # updated_grid = json.dumps({"type":"UPDATE_GRID","content":{"geogriddata":json_data}},separators=(',', ':'))
        # await websocket.send(updated_grid)
        # print(f"Changed the table!")
        ####################

async def main_detection(grid_position_dict):
    """
    Main method of the program, which detects and records info from ArUco markers.
    """
    def sort_data(detected):
        """This sorts through detected markers and determines if it's actually in
        the correct center position of the grid (for ONE frame)

        Parameter is non-empty LIST of [ marker ID, (x, y)]

        Returns a LIST of sorted_markers, LIST of sorted_positions"""

        # Create new lists which will correspond to the correct grid positions
        sorted_markers = []
        sorted_positions = []

        # Determine how many pixels away from the center coordiate a point can be while still being detected
        leeway = 20

        # Each v1 is a tuple (x, y) of the correct center position
        for k1, v1 in list(grid_position_dict.items()):
            found_flag = False
            lower_bound = (v1[0] - leeway, v1[1] - leeway)
            upper_bound = (v1[0] + leeway, v1[1] + leeway)

            if detected != 0:
                # Go through our detected data and see if any of the center positions match
                for elem in detected: #elem is, for example, ( 1, (x,y) )
                    k2 = elem[0] # ArUco marker ID
                    v2 = elem[1] # Position coordinate

                    # If the center position is in range, add the marker ID and the correct center position
                    if lower_bound[0] <= v2[0] <= upper_bound[0] and lower_bound[1] <= v2[1] <= upper_bound[1]:
                        sorted_markers.append(k2)
                        sorted_positions.append(v1)
                        found_flag = True
                        break

            # If position is not in range, then append to the marker ID 'None', at which position
            if found_flag == False:
                sorted_markers.append('None')
                sorted_positions.append(v1)

        # Return the sorted lists
        return sorted_markers, sorted_positions
    async with websockets.connect(deploy_uri, max_size=2**24, compression="deflate") as websocket:
        # Initialize variable to keep track of previous dataframes
        old_output = (None, (None, None))

        # Start the video capture
        input("Place your markers on the grid. Press enter once done. ")
        cap = cv2.VideoCapture(camera)

        # Initialize the dictionary to track frequenices and initialize frame counter
        freq_dict = {}
        frame_counter = 1

        # Create while loop to always be displaying frame and detecting markers
        while True:
            # We collected info from 10 frames --> now let's check
            if frame_counter == 11:
                # Check the frequency dictionary for the 6/10 frame markers
                if len(list(freq_dict.keys())) > 5:
                    # not possible for the same markers to appear in at least 6 frames
                    pass
                else:
                    for k,v in list(freq_dict.items()):
                        if v > 5: # frame appeared at least 6 times
                            output = k # save the tuple of the ( [Marker IDs], [coordinates]) to output

                # Check if this is the same as the old
                if output != old_output: # if the output is different, display new output as dataframe
                    # output is ( [1,2,3], [(x,y), (x,y), (x,y)])
                    data = {"Marker ID": output[0],
                            "Coordinate": output[1]}
                    df = pd.DataFrame(data)
                    # print("-------------------------")
                    print(df)

                    # Prepare the data to be sent
                    json_data = {"DataType": "raw",
                                "Data": data}

                    # Send the JSON data to the WebSocket server
                    await map_for_websocket(json_data)

                # Reset everything
                freq_dict = {}
                frame_counter = 1
                old_output = output
                #await asyncio.sleep(1)

            # Collect info from 10 frames
            else:
                #print(f"Frame #{frame_counter}")

                # Capture one frame and unwarp it
                ret, frame = cap.read()
                frame = unwarping(frame)

                # Detect the markers from one frame
                frame, detected = detect_markers(frame, this_aruco_dictionary, this_aruco_parameters)

                # Sort the list of detected markers
                sorted_markers, sorted_positions = sort_data(detected)
                #print(f"Sorted markers: {sorted_markers}")
                #print(f"Sorted positions: {sorted_positions}")

                # With the organized info, add them to the frequency dictionary, mapping Tuple: Frequency
                datatuple = (tuple(sorted_markers), tuple(sorted_positions))

                if datatuple not in list(freq_dict.keys()):
                    freq_dict[datatuple] = 1
                else:
                    freq_dict[datatuple] += 1

                # Increase frame count
                frame_counter += 1

            cv2.imshow('frame', frame)

            # Create exit button
            if cv2.waitKey(200) & 0xFF == ord('q'):
                break

        # Close down the video stream
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    # Check that we have a valid ArUco marker dictionary.
    # if ARUCO_DICT.get(desired_aruco_dictionary, None) is None:
    #     print("ArUCo tag of '{}' is not supported".format(desired_aruco_dictionary))
    #     cv2.sys.exit(0)

    # Detect the markers
    desired_aruco_dictionary = "DICT_4X4_50"
    rows = 3
    cols = 3
    grid_position_dict = calibrate(desired_aruco_dictionary, rows, cols)
    main_detection(grid_position_dict)
