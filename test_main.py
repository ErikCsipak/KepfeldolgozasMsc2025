import cv2
import numpy as np
import snooker_colors as cr
import ball_detector as bd

# test

capture = cv2.VideoCapture("snooker_720p_sullivan.mp4")

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break

    balls = bd.get_balls_map(frame)

    """if balls is not None:
        balls = np.uint16(np.around(balls.get(cr.RED)))
        for ballList in balls:
            print(ballList)
            for (x, y, r) in ballList:
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # circle around ball
                cv2.circle(frame, (x, y), 2, (255, 0, 0), 3)  # center dot"""

    cv2.imshow("Snooker Red Ball Detection", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()