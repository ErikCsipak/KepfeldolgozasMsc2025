import cv2
import numpy as np

capture = cv2.VideoCapture("snooker_720p_sullivan.mp4")

#red ball
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

current_player = 1          # 1 or 2
ball_to_pot = "Red"         # "Red" or "Color"
previous_red_count = -1     # stores the red count from the last stable frame

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

    current_red_count = 0
    if circles is not None:
        circles = np.uint16(np.around(circles))
        current_red_count = len(circles[0])
        for (x, y, r) in circles[0, :]:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)    # circle around ball
            cv2.circle(frame, (x, y), 2, (255, 0, 0), 3)    # center dot
 
    # check if it is not the first frame
    if previous_red_count != -1:
        
        # detect a successful red pot
        if previous_red_count - current_red_count == 1:
            # logic for red ball scoring
            
            # switch the target ball from Red to Color (player continues turn)
            if ball_to_pot == "Red":
                ball_to_pot = "Color"
            
            # if a red ball was potted instead of color -> turn switch
            else:
                current_player = 1 if current_player == 2 else 2
                # logic for foul penalty
        
        # logic for detecting a miss or foul
        # if shot concluded and no pot:
        current_player = 1 if current_player == 2 else 2
        ball_to_pot = "Red" if current_red_count > 0 else ball_to_pot
        
        # if shot concluded and a Color was potted: ball_to_pot = "Color"
        ball_to_pot = "Red" # player continues turn, must now pot a Red
        
        # if shot concluded and a Color was potted instead of Red (foul)
        current_player = 1 if current_player == 2 else 2
        # logic here to apply penalty points for the foul

    previous_red_count = current_red_count

    # display current state
    cv2.putText(frame, f"Player {current_player}'s Turn. Pot: {ball_to_pot}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Reds Left: {current_red_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # show result
    cv2.imshow("Snooker Red Ball Detection", frame)
    cv2.imshow("Red Mask", mask)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()