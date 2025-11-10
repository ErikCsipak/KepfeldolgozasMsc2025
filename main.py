import cv2
import numpy as np
import snooker_colors as cr
import ball_detector as bd

# test

capture = cv2.VideoCapture("snooker_720p_sullivan.mp4")

current_player = 1          # 1 or 2
ball_to_pot = "Red"         # "Red" or "Color"
previous_red_count = -1     # stores the red count from the last stable frame

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break

    balls = bd.get_balls_map(frame)

    current_red_count = 0
    if balls is not None:
        print(balls)
        balls = np.uint16(np.around(balls.get(cr.WHITE)))
        current_red_count = len(balls[0])
        for (x, y, r) in balls[0, :]:
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
    bgr_boosted = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
    cv2.imshow("Snooker Red Ball Detection", bgr_boosted)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()