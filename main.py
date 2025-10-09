import cv2
import numpy as np

capture = cv2.VideoCapture("video.mp4")

#red ball
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break

    # normalize frame (for speed)
    frame = cv2.resize(frame, (800, 450))
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # optimize for noise reduction
    mask = cv2.GaussianBlur(mask, (9, 9), 2)

    # detect balls
    circles = cv2.HoughCircles(
        mask, 
        cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
        param1=50, param2=15, minRadius=6, maxRadius=15
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (x, y, r) in circles[0, :]:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)   # circle around ball
            cv2.circle(frame, (x, y), 2, (255, 0, 0), 3)   # center dot

    # show result
    cv2.imshow("Snooker Red Ball Detection", frame)
    cv2.imshow("Red Mask", mask)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
