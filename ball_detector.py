import cv2
import snooker_colors as sc
import numpy as np

def _normalize_frame(current_frame):
    """
    Normalizes one frame for better performance
    :param current_frame: current frame of the given video
    :return: a normalized frame in hsv color-space
    """
    f = cv2.resize(current_frame, (1000, 550))
    f = f[70:475, 100:900] # crop image to table
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    #cv2.imshow("frame", hsv)
    #debug_hsv(hsv)

    # Increase saturation
    h, s, v = cv2.split(hsv)
    s = cv2.add(s, 50)  # increase saturation (tune this value)
    s = np.clip(s, 0, 255)
    hsv_sat = cv2.merge([h, s, v])

    return hsv_sat

def debug_hsv(frame):

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("HSV:", frame[y, x])

    cv2.setMouseCallback("frame", mouse_callback)
    cv2.waitKey(0)

def get_balls_map(f):
    """
    Detects the balls of the f frame and returns them in a map.
    Function normalizes frame to hsv color space.

    :param f: the current frame
    :return: map of balls, where key: snooker_colors colors and value: list of balls in the format of HoughCircles
    """
    h_f = _normalize_frame(f)

    return {
        #sc.RED: _detect_balls_in_given_range(h_f, sc.lower_red, sc.upper_red),
        #sc.PINK: _detect_balls_in_given_range(h_f, sc.lower_pink, sc.upper_pink),
        #sc.BLUE: _detect_balls_in_given_range(h_f, sc.lower_blue, sc.upper_blue),
        #sc.GREEN: _detect_balls_in_given_range(h_f, sc.lower_green, sc.upper_green),
        #sc.YELLOW: _detect_balls_in_given_range(h_f, sc.lower_yellow, sc.upper_yellow),
        #sc.BROWN: _detect_balls_in_given_range(h_f, sc.lower_brown, sc.upper_brown),

        # after colors detected
        #sc.WHITE: _detect_balls_in_given_range(h_f, sc.lower_white, sc.upper_white),
        #sc.BLACK: _detect_balls_in_given_range(h_f, sc.lower_black, sc.upper_black),
    }


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
    # optimize for noise reduction
    mask = cv2.GaussianBlur(mask, (9, 9), 2)

    cv2.imshow("Red Mask", mask)
    return cv2.HoughCircles(
        mask,
        cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
        param1=50, param2=15, minRadius=6, maxRadius=15
    )

def _detect_balls_in_given_range(hsv, lower, upper):
    if np.array_equal(lower, sc.lower_red):
        return _detect_red_balls(hsv, lower, upper)
    else:
        mask = cv2.inRange(hsv, lower, upper)

    # remove noise (important!)
    #kernel = np.ones((5, 5), np.uint8)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        cv2.imshow("mask", mask)
    # edge detection
    #edges = cv2.Canny(mask, 50, 150)
    #cv2.imshow("edges", edges)

        circles = cv2.HoughCircles(
            mask,
            cv2.HOUGH_GRADIENT,
            dp=1.3,
            minDist=25,
            param1=100,
            param2=10,        # smaller param2 makes detection more sensitive
            minRadius=4,
            maxRadius=20
        )

    return circles


def _detect_balls_in_given_range(hsv, lower, upper):
    mask = cv2.inRange(hsv, lower, upper)

    # remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    cv2.imshow("mask", mask)
    # find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 50 or area > 2000:   # reject tiny noise & cushion blobs
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * (area / (perimeter * perimeter))

        if circularity > 0.65:  # 1.0 = perfect circle
            (x, y), r = cv2.minEnclosingCircle(cnt)
            if 5 < r < 20:      # expected snooker ball radius
                detected.append((int(x), int(y), int(r)))

    return detected


"""def _detect_balls_in_given_range(hsv, lower, upper):
    
    Detects balls in a given color-range.
    :param hsv: the hsv frame
    :param lower: the lower boundary of the given color
    :param upper: the upper boundary of the given color
    :return: the detected balls
    
    if np.array_equal(lower, sc.lower_red):
        return _detect_red_balls(hsv, lower, upper)
    else:
        cv2.imshow("hsv", hsv)
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.GaussianBlur(mask, (9, 9), 2)
        #if np.array_equal(lower, sc.lower_white):
            #cv2.imshow("mask", mask)

        return cv2.HoughCircles(
            mask,
            cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
            param1=50, param2=15, minRadius=5, maxRadius=20
        )"""