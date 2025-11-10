import cv2
import snooker_colors as sc
import numpy as np

DEBUG = False

def resize_frame(frame):
    return cv2.resize(frame, (1000, 550))

def _normalize_frame(current_frame):
    """
    Normalizes one frame for better performance
    :param current_frame: current frame of the given video
    :return: a normalized frame in hsv color-space
    """
    f = resize_frame(current_frame)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)

    # Increase saturation
    h, s, v = cv2.split(hsv)
    s = cv2.add(s, 50)
    s = np.clip(s, 0, 255)
    hsv_sat = cv2.merge([h, s, v])

    return hsv_sat

def get_balls_map(f):
    """
    Detects the balls of the f frame and returns them in a map.
    Function normalizes frame to hsv color space.

    :param f: the current frame
    :return: map of balls, where key: snooker_colors colors and value: list of balls in the format of HoughCircles
    """
    h_f = _normalize_frame(f)

    return {
        sc.RED: _detect_balls_in_given_range(h_f, sc.lower_red, sc.upper_red),
        sc.PINK: _detect_balls_in_given_range(h_f, sc.lower_pink, sc.upper_pink),
        sc.BLUE: _detect_balls_in_given_range(h_f, sc.lower_blue, sc.upper_blue),
        #sc.GREEN: _detect_balls_in_given_range(h_f, sc.lower_green, sc.upper_green), #todo
        sc.YELLOW: _detect_balls_in_given_range(h_f, sc.lower_yellow, sc.upper_yellow),
        sc.BROWN: _detect_balls_in_given_range(h_f, sc.lower_brown, sc.upper_brown),

        # after colors detected
        sc.WHITE: _detect_balls_in_given_range(h_f, sc.lower_white, sc.upper_white),
        sc.BLACK: _detect_balls_in_given_range(h_f, sc.lower_black, sc.upper_black),
    }

def _find_hough_circles(mask):
    return cv2.HoughCircles(
        mask,
        cv2.HOUGH_GRADIENT, dp=2, minDist=8, # smaller param2 makes detection more sensitive
        param1=50, param2=15, minRadius=5, maxRadius=7
    )

def _detect_red_balls(hsv, l_r, u_r):
    """
    Detects red balls. Separate function needed because red balls are special case for HSV.
    :param l_r: first part of the spectrum's lower red
    :param u_r: first part of the spectrum's upper red
    :param hsv: the hsv frame
    :return: the detected red balls
    """
    mask1 = cv2.inRange(hsv, l_r, u_r)
    mask2 = cv2.inRange(hsv, sc.lower_red2, sc.upper_red2)
    mask = mask1 | mask2

    mask = cv2.GaussianBlur(mask, (3, 3), 2)
    _balls = cv2.HoughCircles(
        mask,
        cv2.HOUGH_GRADIENT, dp=2, minDist=8,
        param1=50, param2=15, minRadius=5, maxRadius=7
    )

    _draw_on_detected_monochrome_balls(mask, _balls)
    return _balls

def _detect_black_ball(hsv, l, u):
    mask = _generate_mask(hsv, l, u)
    mask = _clean_up_mask(mask)
    circles = _find_hough_circles(mask)
    _draw_on_detected_monochrome_balls(mask, circles)
    return circles

def _detect_colored_balls(hsv, l, u):
    mask = _generate_mask(hsv, l, u)
    _balls = _find_hough_circles(mask)
    _draw_on_detected_monochrome_balls(mask, _balls)
    return _balls

def _generate_mask(hsv, l, u):
    return cv2.inRange(hsv, l, u)

def _clean_up_mask(mask):
    #kernel = np.ones((5, 5), np.uint8)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.GaussianBlur(mask, (3, 3), 2)

def _detect_balls_in_given_range(hsv, lower, upper):
    """
    Detects balls based on the lower and upper thresholds.
    Red and black balls are exceptional cases.
    :param hsv: hsv color space frame
    :param lower: lower threshold
    :param upper: upper threshold
    :return: array of ball coordinates (x,y,r)
    """
    if np.array_equal(lower, sc.lower_red):
        return _detect_red_balls(hsv, lower, upper)
    elif np.array_equal(lower, sc.lower_black): # tune this if needed
        return _detect_black_ball(hsv, lower, upper)
    else:
        return _detect_colored_balls(hsv, lower, upper)

def _draw_on_detected_monochrome_balls(frame, balls):
    """
    Note of current implementation: Always draws the last color enabled in the array of balls
    :param frame: frame to draw on
    :param balls: ball to draw
    :return: nothing
    """
    if not DEBUG:
        return
    print(balls)
    if balls is not None:
        _balls = np.uint16(np.around(balls))
        for ballArr in _balls:
            for (x, y, r) in ballArr:
                cv2.circle(frame, (x, y), r, (255, 0, 0), 2)  # circle around ball
                #cv2.circle(frame, (x, y), 2, (255, 0, 0), 3)    # center dot (debug)
    cv2.imshow("Current color", frame)

def draw_detected_balls(frame, balls):
    if balls is not None:
        for key in balls.keys():
            if balls.get(key) is not None:
                ballsList = balls.get(key)[0]
                _balls = np.uint16(np.around(ballsList))
                for ball in _balls:
                    cv2.circle(frame, (ball[0], ball[1]), ball[2], (255, 0, 0), 2)  # circle around ball