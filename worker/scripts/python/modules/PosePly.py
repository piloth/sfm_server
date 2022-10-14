import os
import sys
from logging import getLogger
import collections

import numpy as np
import quaternion
import plyfile


BasePose = collections.namedtuple("Image", ["id", "qvec", "tvec"])

class Pose:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.logger.info("initialized")
        self.pose = {}

    def add(self, image_id, qvec, tvec):
        self.pose[image_id] = BasePose(id=image_id, qvec=qvec, tvec=tvec)

    def savePly(self, outply):
        dtype_v = [
                ('x', 'f4'),
                ('y', 'f4'),
                ('z', 'f4')
                ]
        dtype_f = [
                ('vertex_indices', 'i4', (3,)),
                ('red', 'u1'),
                ('green', 'u1'),
                ('blue', 'u1')
                ]
        # ToDo input from args
        frustum_size = 0.2
        focal = 480
        w = 640
        h = 480
        red = 255
        green = 255
        blue = 0
        # frustum shape
        frustum_d = frustum_size
        frustum_w = w * frustum_size / focal
        frustum_h = h * frustum_size / focal
        # frustum 
        rect_image = [
                [frustum_w * 0.5, frustum_h * 0.5, frustum_d],
                [-frustum_w * 0.5, frustum_h * 0.5, frustum_d],
                [frustum_w * 0.5, -frustum_h * 0.5, frustum_d],
                [-frustum_w * 0.5, -frustum_h * 0.5, frustum_d]
                ]

        vertex = []
        face = []
        v_cnt = 0
        for p in self.pose.values():
            self.logger.info(f"{p}")
            q = np.quaternion(p.qvec[0], p.qvec[1], p.qvec[2], p.qvec[3])
            vertex.append(p.tvec)
            for i in range(4):
                vertex.append(p.tvec + quaternion.rotate_vectors(q, rect_image[i]))
            face.append(([v_cnt, v_cnt+1, v_cnt+2], red, green, blue))
            face.append(([v_cnt, v_cnt+2, v_cnt+3], red, green, blue))
            face.append(([v_cnt, v_cnt+3, v_cnt+4], red, green, blue))
            face.append(([v_cnt, v_cnt+4, v_cnt+1], red, green, blue))
            face.append(([v_cnt+1, v_cnt+2, v_cnt+3], red, green, blue))
            face.append(([v_cnt+2, v_cnt+3, v_cnt+4], red, green, blue))
            v_cnt += 5

        vertex = np.array(list(map(tuple, vertex)), dtype=dtype_v)
        
        face = np.array(list(map(tuple, face)), dtype=dtype_f)
        self.logger.debug(vertex)
        self.logger.debug(face)

        el_v = plyfile.PlyElement.describe(vertex, 'vertex')
        el_f = plyfile.PlyElement.describe(face, 'face')
        plyfile.PlyData([el_v, el_f]).write(outply)


