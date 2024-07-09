import cv2
import os
import numpy as np
import glob
import pickle

camera = 0

# Create 'images' directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Start the video stream
cap = cv2.VideoCapture(camera)

num = 0

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    k = cv2.waitKey(5)

    if k == ord('q'):
        break
    elif k == ord('s'):  # wait for 's' key to save and exit
        cv2.imwrite('images/img' + str(num) + '.png', img)
        print("image saved!")
        num += 1

    cv2.imshow('Img', img)

# Release and destroy all windows before termination
cap.release()
cv2.destroyAllWindows()

input("Images for calibration collected. Press enter to continute.")

chessboardSize = (10, 7)
frameSize = (640, 480)

# Termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1, 2)

size_of_chessboard_squares_mm = 20
objp = objp * size_of_chessboard_squares_mm

# Arrays to store object points and image points from all the images
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane

images = glob.glob('images/*.png')

if not images:
    print("No images found in the specified path.")
else:
    print(f"Found {len(images)} images.")

for image in images:
    img = cv2.imread(image)
    if img is None:
        print(f"Failed to read image: {image}")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, chessboardSize, None)

    # If found, add object points, image points (after refining them)
    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, chessboardSize, corners2, ret)
        cv2.imshow('img', img)
        cv2.waitKey(1000)
    else:
        print(f"Chessboard corners not found in image: {image}")

cv2.destroyAllWindows()

if not objpoints or not imgpoints:
    print("No chessboard corners were detected. Calibration cannot proceed.")
else:
    ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frameSize, None, None)

    # Save the camera calibration result for later use (we won't worry about rvecs / tvecs)
    with open("calibration.pkl", "wb") as f:
        pickle.dump((cameraMatrix, dist), f)
    with open("cameraMatrix.pkl", "wb") as f:
        pickle.dump(cameraMatrix, f)
    with open("dist.pkl", "wb") as f:
        pickle.dump(dist, f)
