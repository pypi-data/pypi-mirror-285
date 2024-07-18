from __future__ import annotations

import math

import cv2


def read_img(path):
    img = cv2.imread(path, 1)
    h, w, d = img.shape
    return img, h, w, d


def scale_img(img, w_scale, h_scale):
    img_scaled = cv2.resize(img, (int(w_scale), int(h_scale)))
    h, w, d = img_scaled.shape
    return img_scaled, h, w, d


def img_cvt_rgb(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, d = img_rgb.shape
    return img_rgb, h, w, d


def img_rotate(img):
    img_rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    h, w, d = img_rotated.shape
    return img_rotated, h, w, d


def img_trim(img, y_min, y_max, x_min, x_max):
    return img[y_min:y_max, x_min:x_max]


def write_img(img, path):
    cv2.imwrite(path, img)
    return 0


def draw_circle(img, x, y, r):
    return cv2.circle(img, (x, y), r, (0, 0, 255), 10)


def find_circle(x, y, circles, min_dist):
    for circle in circles:
        if cal_distance(x, y, circle[0], circle[1]) < min_dist:
            c_x = circle[0]
            c_y = circle[1]
    return c_x, c_y


def cal_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))


def rotate_img(img, h, w, dx, dy):
    theta = math.atan2(dy, dx)
    degree = math.degrees(theta)
    mat = cv2.getRotationMatrix2D((w / 2, h / 2), degree, 1)
    affine_img = cv2.warpAffine(img, mat, (w, h))

    return affine_img, mat
