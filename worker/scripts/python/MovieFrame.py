# std. library
import sys
import os
from logging import getLogger, config

# third party
import numpy as np
import cv2
from commandr import command, Run


@command
def step_decimation(movie_file, step, output_dir):
    """
    extract movie frame by step decimation.
    movie_file - movie file path
    step - decimation step
    output_dir - output directory path
    """
    step = int(step)
    logger = getLogger(__name__)
    logger.info(f"{movie_file}, {step}, {output_dir}")
    # open movie_file
    cap = cv2.VideoCapture(movie_file)
    # get movie fps
    fps = cap.get(cv2.CAP_PROP_FPS)
    logger.info(f"fps: {fps}")
    # create output_dir
    os.makedirs(output_dir, exist_ok=True)
    # extract movie frame
    cnt = 0
    while True:
        ret, frame = cap.read()
        if ret:
            if cnt % step == 0:
                output_file = os.path.join(output_dir, f"{cnt:06d}.png")
                logger.debug(f"output_file: {output_file}")
                cv2.imwrite(output_file, frame)
            cnt += 1
        else:
            return

def get_matching_ratio(frame1, frame2):
    if frame2 is None:
        ratio = 0.0
    else:
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        akaze = cv2.AKAZE_create()
        kp1, des1 = akaze.detectAndCompute(gray1,None)
        kp2, des2 = akaze.detectAndCompute(gray2,None)
        #bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        #matches = bf.match(des1, des2)
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        ratio = 0.5
        good = []
        for m, n in matches:
            if m.distance < ratio * n.distance:
                good.append([m])
        ratio = len(good) / len(kp1)

    return ratio

@command
def matching_decimation(movie_file, overlap_ratio, output_dir):
    overlap_ratio = float(overlap_ratio)
    logger = getLogger(__name__)
    logger.info(f"{movie_file}, {overlap_ratio}, {output_dir}")
    # open movie_file
    cap = cv2.VideoCapture(movie_file)
    # create output_dir
    os.makedirs(output_dir, exist_ok=True)
    cnt = 0
    past_frame = None
    while True:
        ret, frame = cap.read()
        if ret:
            matching_ratio = get_matching_ratio(frame, past_frame)
            logger.debug(f"{cnt} {matching_ratio}")
            if matching_ratio < overlap_ratio:
                output_file = os.path.join(output_dir, f"{cnt:06d}.png")
                logger.debug(f"output_file: {output_file}")
                cv2.imwrite(output_file, frame)
                past_frame = frame
            cnt += 1
        else:
            return

if __name__ == "__main__":
    # logger from config file
    config.fileConfig(os.path.join(os.path.dirname(__file__), 'logconf.ini'))
    logger = getLogger(__name__)
    Run()
