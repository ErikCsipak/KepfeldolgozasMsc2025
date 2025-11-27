import cv2
import numpy as np
import snooker_colors as cr
import ball_detector as bd

capture = cv2.VideoCapture("snooker.mp4")

current_player = 1          # 1 or 2
ball_to_pot = "Red"         # "Red" or "Color"
previous_red_count = -1     # stores the red count from the last stable frame
previous_white_count = -1   # cue ball
first_score = 0             # score of player 1
second_score = 0            # score of player 2

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break
    frame = bd.resize_frame(frame)

    balls = bd.get_balls_map(frame)

    current_red_count = len(balls.get(cr.RED)[0]) if balls.get(cr.RED) is not None else 0
    current_white_count = len(balls.get(cr.WHITE)[0]) if balls.get(cr.WHITE) is not None else 0

    #bd.draw_detected_balls(frame, balls)

    # check if it is not the first frame
    if previous_red_count != -1:

        red_difference = previous_red_count - current_red_count
        white_difference = previous_white_count - current_white_count

        turn_ended = False

        # case 1: a red was potted
        if red_difference == 1:
            if current_player == 1:
                first_score += 1
            else:
                second_score += 1

            # correct pot -> continue turn
            ball_to_pot = "Color" if ball_to_pot == "Red" else "Red"

        # case 2: no red potted -> miss
        elif red_difference == 0:
            turn_ended = True

        # case 3: more than one red lost -> foul or detection issue
        else:
            turn_ended = True

        # case 4: Cue ball foul (white disappears)
        if white_difference == 1:
            # simple foul = 4 points awarded to opponent
            if current_player == 1:
                second_score += 4
            else:
                first_score += 4

            turn_ended = True

        # switch turn if needed
        if turn_ended:
            current_player = 1 if current_player == 2 else 2
            ball_to_pot = "Red"

    previous_red_count = current_red_count
    previous_white_count = current_white_count

    # display current state
    cv2.putText(frame, f"Player {current_player}'s Turn. Pot: {ball_to_pot}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Reds Left: {current_red_count}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Player 1: {first_score}", (850, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Player 2: {second_score}", (850, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # show result
    #bg.draw_balls_to_frame(frame, balls)
    cv2.imshow("Snooker Red Ball Detection", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
