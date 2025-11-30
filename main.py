import cv2
import numpy as np
from fontTools.ttLib.tables.C_P_A_L_ import Color

import snooker_colors as cr
import ball_detector as bd
import pot_detector as pd

capture = cv2.VideoCapture("snooker_cut.mp4")

current_player = 1          # 1 or 2
ball_to_pot = "Red"         # "Red" or "Color"
previous_red_count = -1     # stores the red count from the last stable frame
first_score = 0             # score of player 1
second_score = 0            # score of player 2
successful = False          # indicates if there was a successful pot
penalty = False             # indicates if there was a foul
frames_without_action = 0   # counter for frames with no pot or change
INACTIVITY_THRESHOLD = 60   # number of frames to wait before switching turn (about 2-3 seconds at 30fps)

# Motion detection variables
previous_frame_gray = None
MOTION_THRESHOLD = 10      # threshold for detecting motion (sum of differences)
frames_without_motion = 0   # counter for frames without ball motion
MOTION_INACTIVITY_THRESHOLD = 90  # frames to wait without motion before turn switch (about 3 seconds at 30fps)

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break
    frame = bd.resize_frame(frame)

    balls = bd.get_balls_map(frame)

    marked_color = pd.get_potted_color(balls)

    current_red_count = len(balls.get(cr.RED)[0])
    #bd.draw_detected_balls(frame, balls) # enable if you want to see the detected balls
 
    # motion detection logic
    current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    current_frame_gray = cv2.GaussianBlur(current_frame_gray, (21, 21), 0)
    
    motion_detected = False
    if previous_frame_gray is not None:
        # calculate frame difference
        frame_diff = cv2.absdiff(previous_frame_gray, current_frame_gray)
        
        # apply threshold to get binary image
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        # calculate motion score (sum of white pixels)
        motion_score = np.sum(thresh) / 255  # normalize by dividing by 255
        
        # check if motion exceeds threshold
        if motion_score > MOTION_THRESHOLD:
            motion_detected = True
            frames_without_motion = 0
        else:
            frames_without_motion += 1
    
    previous_frame_gray = current_frame_gray.copy()
    
    # check if it is not the first frame
    if previous_red_count != -1:

        # detect a red ball missing, starting buffer
        if previous_red_count - current_red_count == 1:
            pd.red_buffer += 1
        else:
            pd.red_buffer = 0
        
        # detect a successful red pot
        if pd.red_buffer == 10:
            previous_red_count = current_red_count
            pd.red_buffer = 0
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
        # if a color ball is missing for a frame
        if len(marked_color) > 0:
            if "pink" in marked_color:  # and "pink" not in potted_color:
                pd.pink_buffer += 1
            else:
                pd.pink_buffer = 0
            if "blue" in marked_color:  # and "blue" not in potted_color:
                pd.blue_buffer += 1
            else:
                pd.blue_buffer = 0
            if "green" in marked_color:  # and "green" not in potted_color:
                 pd.green_buffer += 1
            else:
                pd.green_buffer = 0
            if "yellow" in marked_color:  # and "yellow" not in potted_color:
                pd.yellow_buffer += 1
            else:
                pd.yellow_buffer = 0
            if "brown" in marked_color:  # and "brown" not in potted_color:
                pd.brown_buffer += 1
            else:
                pd.brown_buffer = 0
            if "black" in marked_color:  # and "black" not in potted_color:
                pd.black_buffer += 1
            else:
                pd.black_buffer = 0
            if "white" in marked_color:  # and "white" not in potted_color:
                pd.white_buffer += 1
            else:
                pd.white_buffer = 0

            potted_color_confirmed = pd.pot_confirm()
            if potted_color_confirmed != "none":
                if potted_color_confirmed == "white":
                # applying penalty for potting white ball
                    if current_player == 2:
                        first_score += 4
                    else:
                        second_score += 4
                    current_player = 1 if current_player == 2 else 2
                if ball_to_pot == "Color":
                    if current_player == 1:
                        first_score += pd.points[potted_color_confirmed]
                    else:
                        second_score += pd.points[potted_color_confirmed]
                    ball_to_pot = "Red"  # player continues turn, must now pot a Red
                else:
                    # if shot concluded and a Color was potted instead of Red (foul)
                    if current_player == 2:
                        first_score += max(pd.points[potted_color_confirmed], 4)
                    else:
                        second_score += max(pd.points[potted_color_confirmed], 4)
                    current_player = 1 if current_player == 2 else 2
                    ball_to_pot = "Red"
        
        # logic for start of new turn
        if successful and not penalty:
            if ball_to_pot == "Red":
                ball_to_pot = "Color"
            else:
                ball_to_pot = "Red"
            frames_without_motion = 0  # reset motion counter on successful pot
        
        # turn switch based on motion detection (no balls moving)
        if frames_without_motion >= MOTION_INACTIVITY_THRESHOLD:
            current_player = 1 if current_player == 2 else 2
            ball_to_pot = "Red" if current_red_count > 0 else ball_to_pot
            frames_without_motion = 0  # reset counter after turn switch
            successful = False
            penalty = False
    else:
        previous_red_count = current_red_count

    successful = False  # reset for next frame
    penalty = False     # reset for next frame

    # display current state
    motion_status = "MOVING" if motion_detected else "STILL"
    cv2.putText(frame, f"Player {current_player}'s Turn. Pot: {ball_to_pot}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Reds Left: {current_red_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Motion: {motion_status} ({frames_without_motion})", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Player 1: {first_score}", (850, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Player 2: {second_score}", (850, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # show result
    #bg.draw_balls_to_frame(frame, balls)
    cv2.imshow("Snooker Red Ball Detection", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()