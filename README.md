Libraries used: OpenCV - 4.10.0, NumPy - 2.0.0, and Pandas 2.2.2.

About "aruco marker data collector":

This file detects ArUco markers on a grid and saves information about the ArUco ID, the index (position of the ArUco on the grid), and the coordinate of each ArUco marker detected.

1. Before using "aruco marker data collector," run the file "calibration matrix generator" to determine the camera's warping properties. (Note: you will need a chessboard size of 10 by 7). This will save a matrix that will be used in "aruco marker data collector" to unwarp the camera view when detecting the ArUco markers.

2. Run "aruco marker data collector." The first part of the code will "calibrate" the camera by determining what size grid you want to detect markers on. Then, you will need to place ArUco markers in each corner of the grid. To close the window, press 'q'.

3. Afterwards, the code will capture 10 frames at a time, printing a dataframe that displays ArUco markers detected in 6 out of the 10 frames. There will be a prompt if you want to save the dataframe as a JSON file.

4. The code will only print dataframes if the ArUco markers detected are different than the previous ones detected (from the most recent 10 frame snapshot).

5. To close the window and terminate the detection, press 'q'.
