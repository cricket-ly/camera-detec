import cv2
import pandas as pd
import numpy as np
import pickle
from update_global_with_local import *

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

def get_int_input(prompt):
    """ Get an integer input from the user. """
    while True:
        try:
            value = int(input(prompt))
            if value > 1:
                return value
            else:
                print("Invalid input. Please enter an integer greater than 1.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def detect_markers(frame, this_aruco_dictionary, this_aruco_parameters):
    """Detects the markers in one frame and draws the marker borders.

    Returns the drawn on frame and a LIST of markers that were detected"""
    # Detect ArUco markers in the frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(
        frame, this_aruco_dictionary, parameters=this_aruco_parameters)

    # Initialize list of detected markers and their center position
    detected = []

    # Check that at least one ArUco marker was detected
    if ids is not None:
        # Flatten the ArUco IDs list
        ids = ids.flatten()

        # Loop over the detected ArUco corners
        for (marker_corner, marker_id) in zip(corners, ids):
            # Extract the marker corners
            corners = marker_corner.reshape((4, 2))
            (top_left, top_right, bottom_right, bottom_left) = corners

            # Convert the (x,y) coordinate pairs to integers
            top_right = (int(top_right[0]), int(top_right[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
            top_left = (int(top_left[0]), int(top_left[1]))

            # Draw the bounding box of the ArUco detection
            cv2.line(frame, top_left, top_right, (0, 255, 0), 2)
            cv2.line(frame, top_right, bottom_right, (0, 255, 0), 2)
            cv2.line(frame, bottom_right, bottom_left, (0, 255, 0), 2)
            cv2.line(frame, bottom_left, top_left, (0, 255, 0), 2)

            # Calculate and draw the center of the ArUco marker
            center_x = int((top_left[0] + bottom_right[0]) / 2.0)
            center_y = int((top_left[1] + bottom_right[1]) / 2.0)
            cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1)

            # Save this Marker ID and center position in our list
            detected.append( (int(marker_id), (center_x,center_y)) )

            # Draw the ArUco marker ID on the video frame
            # The ID is always located at the top_left of the ArUco marker
            cv2.putText(frame, str(marker_id),
                        (top_left[0], top_left[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
    #else:
    #    print("[ERROR] During detect_markers(frame), no markers were found.")

    return frame, detected

def get_coordinates(desired_aruco_dictionary):
    """ Gets the center coordinates of the ArUco markers detected.

    Parameter is a STRING of the name of the ArUco dictionary to detect.

    Returns a LIST of tuples, with each tuple containing integers of ( Marker ID, (x, y) )"""
    this_aruco_dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT[desired_aruco_dictionary])
    this_aruco_parameters = cv2.aruco.DetectorParameters()

    # Start the video stream
    cap = cv2.VideoCapture(camera)


    while True:
        ret, frame = cap.read()
        frame = unwarping(frame)

        frame, detected = detect_markers(frame, this_aruco_dictionary, this_aruco_parameters)

        # Display the resulting frame
        cv2.imshow('frame', frame)

        ## Display the detected
        # print(f"Detected: {detected}")

        # If "q" is pressed on the keyboard, exit this loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close down the video stream
    cap.release()
    cv2.destroyAllWindows()

    # Return our list with Marker ID and coordinate
    return detected

def generate_matrix(top_L, top_R, bottom_L, bottom_R, rows, cols):
    """
    Generate a matrix of coordinate points.

    Parameters:
    top_L (tuple): Top left coordinate (x, y)
    top_R (tuple): Top right coordinate (x, y)
    bottom_L (tuple): Bottom left coordinate (x, y)
    bottom_R (tuple): Bottom right coordinate (x, y)
    rows (int): Number of rows in the matrix
    cols (int): Number of columns in the matrix

    Returns:
    np.array: Matrix of coordinate points
    """
    # Generate the left and right column coordinates
    left_column = np.linspace(top_L, bottom_L, rows)
    right_column = np.linspace(top_R, bottom_R, rows)

    # Interpolate the points between the left and right columns
    matrix = np.zeros((rows, cols, 2))
    for i in range(rows):
        matrix[i, :, :] = np.linspace(left_column[i], right_column[i], cols)

    return matrix

def matrix_to_dict(matrix, rows, columns):
    """Transfers information in a matrix into a dictionary.

    Parameter: The matrix to change.

    Returns: A DICT which maps the marker position in the grid (starting from 0) to the coordinate. """
    #Initialize dictionary to return
    grid_dict = {}
    position_counter = 0

    # Go row by row in the matrix and add the coordinate to the dictionary
    for n in range(rows): # if rows = 4, n = 0, 1, 2, 3
        row = matrix[n, :, :]
        for coordinate in row: # one coordinate is [x, y]
            # Change coordinates to integers in a tuple
            coordinate = (int(coordinate[0]), int(coordinate[1]))
            grid_dict[position_counter] = tuple(coordinate)
            position_counter += 1
        n += 1

    # Verify grid_dict is the correct length
    assert len(grid_dict) == rows*columns, "Error in establishing dictionary."

    return grid_dict

def unwarping(frame):
    """Unwarps a frame (object of type NumPy array) and returns the new, unwarped frame."""
    # Load the camera calibration result from the saved files
    with open("cameraMatrix.pkl", "rb") as f:
        cameraMatrix = pickle.load(f)
    with open("dist.pkl", "rb") as f:
        dist = pickle.load(f)

    # Read the frame that we want undistorted
    """Need to think about what parameters we want here"""
    #img = cv2.imread('images/img1.png')
    img = frame
    # if img is None:
    #     print("Failed to load image.")
    # else:
    h, w = img.shape[:2]

    # Compute the new camera matrix and undistort the image
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w, h), 1, (w, h))
    dst = cv2.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

    # Crop the image (if necessary)
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    # Display the undistorted image
    #cv2.imwrite('caliResult1.png', dst)
    #print("Undistorted image saved as 'caliResult1.png'.")

    return dst

def ThresWin(parameters, min, max, step):
    parameters.adaptiveThreshWinSizeMin = min
    parameters.adaptiveThreshWinSizeMax = max
    parameters.adaptiveThreshWinSizeStep = step
