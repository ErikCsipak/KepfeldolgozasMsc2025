import cv2
import numpy as np
from fontTools.ttLib.tables.C_P_A_L_ import Color

import snooker_colors as cr
import ball_detector as bd
import pot_detector as pd

capture = cv2.VideoCapture("snooker.mp4")

current_player = 1          # 1 or 2
ball_to_pot = "Red"         # "Red" or "Color"
previous_red_count = -1     # stores the red count from the last stable frame
first_score = 0             # score of player 1
second_score = 0            # score of player 2
successful = False          # indicates if there was a successful pot
penalty = False             # indicates if there was a foul

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break
    frame = bd.resize_frame(frame)

    balls = bd.get_balls_map(frame)

    potted_color = pd.get_potted_color(balls)

    current_red_count = len(balls.get(cr.RED)[0])
    bd.draw_detected_balls(frame, balls) # enable if you want to see the detected balls
 
    # check if it is not the first frame
    if previous_red_count != -1:
        
        # detect a successful red pot
        if previous_red_count - current_red_count == 1:
            # switch the target ball from Red to Color (player continues turn)
            if ball_to_pot == "Red":
                successful = True
                if current_player == 1:
                    first_score += 1
                else:
                    second_score += 1
            
            # if a red ball was potted instead of color -> turn switch
            else:
                # logic for foul penalty
                penalty = True   # failsafe in case of both a red and color was potted
                if current_player == 2:
                    first_score += 4
                else:
                    second_score += 4

        # if shot concluded and a Color was potted: ball_to_pot = "Color" (todo: currently does not check if multiple color balls are potted in one frame)
        if len(potted_color) > 0:
            if ball_to_pot == Color:
                if current_player == 1:
                    first_score += pd.points[potted_color[0]]
                else:
                    second_score += pd.points[potted_color[0]]
                successful = True
                ball_to_pot = "Red"  # player continues turn, must now pot a Red
            else:
                # if shot concluded and a Color was potted instead of Red (foul)
                penalty = True  # failsafe in case of both a red and color was potted
                if current_player == 2:
                    first_score += max(pd.points[potted_color[0]], 4)
                else:
                    second_score += max(pd.points[potted_color[0]], 4)
        
        # logic for detecting a miss or foul

        # logic for start of new turn
        if successful and not penalty:
            if ball_to_pot == "Red":
                ball_to_pot = "Color"
            else:
                ball_to_pot = "Red"
        else:
            # if shot concluded and no pot:
            current_player = 1 if current_player == 2 else 2
            ball_to_pot = "Red" if current_red_count > 0 else ball_to_pot

    previous_red_count = current_red_count

    # display current state
    cv2.putText(frame, f"Player {current_player}'s Turn. Pot: {ball_to_pot}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Reds Left: {current_red_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Player 1: {first_score}", (850, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Player 2: {second_score}", (850, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # show result
    #bg.draw_balls_to_frame(frame, balls)
    cv2.imshow("Snooker Red Ball Detection", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()