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


if __name__ == "__main__":
    # logger from config file
    config.fileConfig(os.path.join(os.path.dirname(__file__), 'logconf.ini'))
    logger = getLogger(__name__)
    Run()
