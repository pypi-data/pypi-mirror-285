from __future__ import annotations

import cv2
import numpy as np

from module_qc_nonelec_gui.qc_tests.vi.functions.cv2_func import cal_distance, math


def detect_circle(img):
    h, w, c = img.shape
    # remove blue pixel
    for i in range(h):
        for j in range(w):
            img.itemset((i, j, 0), 0)

    # get gray image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # Circle detection with Hough Transformation
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        1,
        100,
        param1=100,
        param2=50,
        minRadius=50,
        maxRadius=70,
    )
    circles = np.uint16(np.around(circles))

    # sort with y col
    col_num = 1
    circles = circles[0, :]
    return circles[np.argsort(circles[:, col_num])]


def find_edge(img, circles, mini_ref_points1, mini_ref_points2, config):
    h, w, c = img.shape

    # get interesting circles
    x = circles[:, 0]
    x_hist, x_bins = np.histogram(x, bins=20)
    ref_line_x = []
    for i, x_value in enumerate(x_hist):
        if x_value > 6:
            ref_line_x.append([x_bins[i], x_bins[i + 1]])

    # get reference points
    points = {}
    for i, p in enumerate(ref_line_x):
        n = 0
        for circle in circles:
            if p[0] < circle[0] and circle[0] < p[1]:
                n = n + 1
                if n == 1:
                    points[i] = circle.reshape(1, -1)
                else:
                    points[i] = np.vstack([points[i], circle.reshape(1, -1)])

    # calculate rotation angle
    nmatch = 0
    dx = 0
    dy = 0
    matched_points = {}
    distance = 100
    for circle1 in points[0]:
        for circle2 in points[1]:
            if abs(int(circle1[1]) - int(circle2[1])) < distance:
                nmatch = nmatch + 1
                dx = dx - int(circle1[0]) + int(circle2[0])
                dy = dy - int(circle1[1]) + int(circle2[1])
                if nmatch == 1:
                    matched_points[0] = circle1.reshape(1, -1)
                    matched_points[1] = circle2.reshape(1, -1)
                else:
                    matched_points[0] = np.vstack(
                        [matched_points[0], circle1.reshape(1, -1)]
                    )
                    matched_points[1] = np.vstack(
                        [matched_points[1], circle2.reshape(1, -1)]
                    )
    missing_point = -1
    if nmatch == 5:
        if points[0].shape[0] > 6:
            for i, circle1 in enumerate(points[0]):
                for circle2 in points[1]:
                    if abs(int(circle1[1]) - int(circle2[1])) < distance:
                        pass
                    else:
                        if i not in [3, 4]:
                            missing_point = i
        elif points[1].shape[0] > 6:
            for i, circle1 in enumerate(points[1]):
                for circle2 in points[0]:
                    if abs(int(circle1[1]) - int(circle2[1])) < distance:
                        pass
                    else:
                        if i not in [3, 4]:
                            missing_point = i

    dx = dx / nmatch
    dy = dy / nmatch
    theta = math.atan2(dy, dx)
    degree = math.degrees(theta)

    # rotate image
    mat = cv2.getRotationMatrix2D((w / 2, h / 2), degree, 1)
    # affine_img = cv2.warpAffine(img, mat, (w, h))

    for i in range(nmatch):
        a0 = np.vstack([matched_points[0][i, :2].reshape(2, 1), 1])
        a1 = np.vstack([matched_points[1][i, :2].reshape(2, 1), 1])
        a0 = np.dot(mat, a0)
        a1 = np.dot(mat, a1)

        matched_points[0][i, :2] = a0[:2,].reshape(1, 2)
        matched_points[1][i, :2] = a1[:2,].reshape(1, 2)

    if nmatch == 6:
        p00_x = int(matched_points[0][0, 0])
        p00_y = int(matched_points[0][0, 1])
        p01_x = int(matched_points[1][0, 0])
        p01_y = int(matched_points[1][0, 1])
        p50_x = int(matched_points[0][5, 0])
        p50_y = int(matched_points[0][5, 1])
        p51_x = int(matched_points[1][5, 0])
        p51_y = int(matched_points[1][5, 1])

        ref_p00_x = int(mini_ref_points1[0, 0])
        ref_p00_y = int(mini_ref_points1[0, 1])
        ref_p01_x = int(mini_ref_points2[0, 0])
        ref_p01_y = int(mini_ref_points2[0, 1])
        ref_p50_x = int(mini_ref_points1[5, 0])
        ref_p50_y = int(mini_ref_points1[5, 1])
        ref_p51_x = int(mini_ref_points2[5, 0])
        ref_p51_y = int(mini_ref_points2[5, 1])

    elif nmatch == 5:
        if missing_point == 0:
            p00_x = int(matched_points[0][0, 0])
            p00_y = int(matched_points[0][0, 1])
            p01_x = int(matched_points[1][0, 0])
            p01_y = int(matched_points[1][0, 1])
            p50_x = int(matched_points[0][4, 0])
            p50_y = int(matched_points[0][4, 1])
            p51_x = int(matched_points[1][4, 0])
            p51_y = int(matched_points[1][4, 1])

            ref_p00_x = int(mini_ref_points1[1, 0])
            ref_p00_y = int(mini_ref_points1[1, 1])
            ref_p01_x = int(mini_ref_points2[1, 0])
            ref_p01_y = int(mini_ref_points2[1, 1])
            ref_p50_x = int(mini_ref_points1[5, 0])
            ref_p50_y = int(mini_ref_points1[5, 1])
            ref_p51_x = int(mini_ref_points2[5, 0])
            ref_p51_y = int(mini_ref_points2[5, 1])
        elif missing_point in [6, 7]:
            p00_x = int(matched_points[0][0, 0])
            p00_y = int(matched_points[0][0, 1])
            p01_x = int(matched_points[1][0, 0])
            p01_y = int(matched_points[1][0, 1])
            p50_x = int(matched_points[0][4, 0])
            p50_y = int(matched_points[0][4, 1])
            p51_x = int(matched_points[1][4, 0])
            p51_y = int(matched_points[1][4, 1])

            ref_p00_x = int(mini_ref_points1[0, 0])
            ref_p00_y = int(mini_ref_points1[0, 1])
            ref_p01_x = int(mini_ref_points2[0, 0])
            ref_p01_y = int(mini_ref_points2[0, 1])
            ref_p50_x = int(mini_ref_points1[4, 0])
            ref_p50_y = int(mini_ref_points1[4, 1])
            ref_p51_x = int(mini_ref_points2[4, 0])
            ref_p51_y = int(mini_ref_points2[4, 1])
        else:
            p00_x = int(matched_points[0][0, 0])
            p00_y = int(matched_points[0][0, 1])
            p01_x = int(matched_points[1][0, 0])
            p01_y = int(matched_points[1][0, 1])
            p50_x = int(matched_points[0][4, 0])
            p50_y = int(matched_points[0][4, 1])
            p51_x = int(matched_points[1][4, 0])
            p51_y = int(matched_points[1][4, 1])

            ref_p00_x = int(mini_ref_points1[0, 0])
            ref_p00_y = int(mini_ref_points1[0, 1])
            ref_p01_x = int(mini_ref_points2[0, 0])
            ref_p01_y = int(mini_ref_points2[0, 1])
            ref_p50_x = int(mini_ref_points1[5, 0])
            ref_p50_y = int(mini_ref_points1[5, 1])
            ref_p51_x = int(mini_ref_points2[5, 0])
            ref_p51_y = int(mini_ref_points2[5, 1])

    d1 = cal_distance(p00_x, p00_y, p50_x, p50_y)
    d2 = cal_distance(p00_x, p00_y, p01_x, p01_y)
    d3 = cal_distance(p00_x, p00_y, p51_x, p51_y)

    d1_ref = cal_distance(ref_p00_x, ref_p00_y, ref_p50_x, ref_p50_y)
    d2_ref = cal_distance(ref_p00_x, ref_p00_y, ref_p01_x, ref_p01_y)
    d3_ref = cal_distance(ref_p00_x, ref_p00_y, ref_p51_x, ref_p51_y)

    scale = (d1 / d1_ref + d2 / d2_ref + d3 / d3_ref) / 3

    xs = (int(p00_x) + int(p50_x)) / 2 - scale * (int(ref_p00_x) + int(ref_p50_x)) / 2
    xe = (int(p01_x) + int(p51_x)) / 2 + scale * (
        config["width"] - (int(ref_p01_x) + int(ref_p51_x)) / 2
    )
    xs = max(xs, 0)
    xe = min(xe, w)

    ys = (int(p00_y) + int(p01_y)) / 2 - scale * (int(ref_p00_y) + int(ref_p01_y)) / 2
    ye = (int(p50_y) + int(p51_y)) / 2 + scale * (
        config["height"] - (int(ref_p50_y) + int(ref_p51_y)) / 2
    )
    ys = max(ys, 0)
    ye = min(ye, h)

    # img_trim = img_affine[int(ys):int(ye),int(xs):int(xe)]

    # return img_trim
    return dx, dy, ys, ye, xs, xe
