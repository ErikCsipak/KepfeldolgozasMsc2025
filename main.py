import cv2
import numpy as np
import snooker_colors as cr

capture = cv2.VideoCapture("snooker_720p_sullivan.mp4")

current_player = 1          # 1 or 2
ball_to_pot = "Red"         # "Red" or "Color"
previous_red_count = -1     # stores the red count from the last stable frame


def normalize_frame(current_frame):
    """
    Normalizes one frame for better performance
    :param current_frame: current frame of the given video
    :return: a normalized frame in hsv color-space
    """
    f = cv2.resize(current_frame, (800, 450))
    return cv2.cvtColor(f, cv2.COLOR_BGR2HSV)

def detect_balls(h_f):
    """
    Detects the balls of the h_f frame and returns them in a list.
    :param h_f: the hsv frame
    :return: list of balls
    """
    return {
        cr.RED: detect_balls_in_given_range(h_f, cr.lower_red, cr.upper_red),
        cr.GREEN  : detect_balls_in_given_range(h_f, cr.lower_green, cr.upper_green),
        cr.BLUE  : detect_balls_in_given_range(h_f, cr.lower_blue, cr.upper_blue),
        cr.BROWN  : detect_balls_in_given_range(h_f, cr.lower_brown, cr.upper_brown),
        cr.YELLOW  : detect_balls_in_given_range(h_f, cr.lower_yellow, cr.upper_yellow),
        cr.PINK  : detect_balls_in_given_range(h_f, cr.lower_pink, cr.upper_pink),
        cr.BLACK  : detect_balls_in_given_range(h_f, cr.lower_black, cr.upper_black),
        cr.WHITE  : detect_balls_in_given_range(h_f, cr.lower_white, cr.upper_white)
    }



def detect_red_balls(hsv, l_r, u_r):
    """
    Detects red balls. Separate function needed because red balls are special case for HSV.
    :param l_r: first part of the spectrum's lower red
    :param u_r: first part of the spectrum's upper red
    :param hsv: the hsv frame
    :return: the detected red balls
    """
    mask1 = cv2.inRange(hsv, l_r, u_r)
    mask2 = cv2.inRange(hsv, cr.lower_red2, cr.upper_red2)
    mask = mask1 | mask2
    # optimize for noise reduction
    mask = cv2.GaussianBlur(mask, (9, 9), 2)
    # detect balls
    cv2.imshow("Red Mask", mask)
    return cv2.HoughCircles(
        mask,
        cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
        param1=50, param2=15, minRadius=6, maxRadius=15
    )

def detect_balls_in_given_range(hsv, lower, upper):
    """
    Detects balls in a given color-range.
    :param hsv: the hsv frame
    :param lower: the lower boundary of the given color
    :param upper: the upper boundary of the given color
    :return: the detected balls
    """
    if np.array_equal(lower, cr.lower_red):
        return detect_red_balls(hsv, lower, upper)
    else:
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.GaussianBlur(mask, (9, 9), 2)

        return cv2.HoughCircles(
            mask,
            cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
            param1=50, param2=15, minRadius=6, maxRadius=15
        )

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break

    hsv_frame = normalize_frame(frame)
    balls = detect_balls(hsv_frame)

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
    cv2.imshow("Snooker Red Ball Detection", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()