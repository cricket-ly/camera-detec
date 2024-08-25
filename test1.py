import websockets
from testcompile import handle_client
import cv2
import pandas as pd
from side_functions import *
from mapping_markers import mapping_markers_to_data

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

async def function_a(grid_position_dict):
    async with websockets.connect(deploy_uri, max_size=2**24, compression="deflate") as websocket:
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
                if output != old_output: # if the output is different, save new output as dataframe
                    data = {"Marker ID": output[0],
                            "Coordinate": output[1]}

                    # Map the data
                    json_data = {"DataType": "raw",
                                "Data": data}
                    info = mapping_markers_to_data(json_data)

                    # Send the information to handle_client()
                    print("Yes, recevied from test1")
                    await handle_client("A", info)

                # Reset everything
                freq_dict = {}
                frame_counter = 1
                old_output = output

            else:
                # Detect the markers in one frame
                ret, frame = cap.read()
                frame = unwarping(frame)
                frame, detected = detect_markers(frame, this_aruco_dictionary, this_aruco_parameters)

                # Sort the list of detected markers
                sorted_markers, sorted_positions = sort_data(detected)

                # Track the marker frequency
                datatuple = (tuple(sorted_markers), tuple(sorted_positions))
                if datatuple not in list(freq_dict.keys()):
                    freq_dict[datatuple] = 1
                else:
                    freq_dict[datatuple] += 1
                frame_counter += 1

            # Show the frame and create exit button
            cv2.imshow('frame', frame)
            if cv2.waitKey(200) & 0xFF == ord('q'):
                break

        # Close down the video stream
        cap.release()
        cv2.destroyAllWindows()
