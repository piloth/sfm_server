# std. library
import sys
import os
from enum import Enum
from logging import config, getLogger

# third party
from commandr import command, Run

# modules
from modules.SSHRunner import SSHRunner



class CameraMode(Enum):
    AUTO = 0
    SINGLE = 1
    PER_FOLDER = 2 
    PER_IMAGE = 3


class Colmap:
    def __init__(self, ws_path):
        self.ws_path = ws_path
        self.database_path = os.path.join(ws_path, "database.db")
        self.sparse_path = os.path.join(ws_path, "sparse")
        os.makedirs(ws_path, exist_ok=True)
        self.mask_path = None
        self.logger = getLogger(__name__)

    def run(self, cmd):
        self.logger.debug(f"{cmd}")
        
        ssh = SSHRunner()
        ssh.connect(hostname="colmap", port=20022, username="root", key_filename="/root/.ssh/id_rsa")
        ret = ssh.run(f"{cmd}")
        if ret != 0:
            self.logger.error(f"command failed with return code {ret}: {cmd}")
            raise RuntimeError(f"command failed with return code {ret}: {cmd}")

    def set_images(self, image_path):
        self.image_path = image_path

    def set_mask_images(self, mask_path):
        self.mask_path = mask_path

    def automatic_reconstructor(self, data_type="video", quality="medium", dense=1):
        """
        colmap automatic_reconstructor --workspace_path colmap_ws --image_path step10 --data_type video --quality medium
        """
        args = ["colmap automatic_reconstructor"]
        #args.append("--single_camera 1")
        args.append(f"--workspace_path {self.ws_path}")
        args.append(f"--dense {dense}")
        #args.append(f"--num_threads 2")
        args.append(f"--image_path {self.image_path}")
        if self.mask_path is not None:
            args.append(f"--mask_path {self.mask_path}")
        args.append(f"--data_type {data_type}")
        args.append(f"--quality {quality}")
        args.append(f"--vocab_tree_path /root/vocab_tree_flickr100K_words32K.bin")
        self.run(" ".join(args))

    def my_reconstructor(self, data_type="video", quality="medium"):
        args = ["colmap feature_extractor"]
        args.append(f"--database_path {self.database_path}")
        args.append(f"--image_path {self.image_path}")
        args.append(f"--SiftExtraction.estimate_affine_shape 1")
        args.append(f"--SiftExtraction.domain_size_pooling 1")
        args.append("--camera_mode 2")
        args.append("--SiftExtraction.max_image_size 1000")
        self.run(" ".join(args))

        args = ["colmap sequential_matcher"]
        args.append(f"--database_path {self.database_path}")
        #args.append(f"--SiftMatching.num_threads 2")
        args.append("--SequentialMatching.vocab_tree_path /root/vocab_tree_flickr100K_words32K.bin")
        args.append("--SequentialMatching.loop_detection 1")
        args.append("--SiftMatching.guided_matching 1")
        args.append("--SiftMatching.max_num_matches 11000")
        self.run(" ".join(args))

        args = ["colmap transitive_matcher"]
        args.append(f"--database_path {self.database_path}")
        self.run(" ".join(args))

        os.makedirs(self.sparse_path, exist_ok=True)
        args = ["colmap mapper"]
        args.append(f"--database_path {self.database_path}")
        args.append(f"--image_path {self.image_path}")
        args.append(f"--output_path {self.sparse_path}")
        args.append("--Mapper.ba_refine_principal_point 1")
        #args.append("--Mapper.multiple_models 0")
        #args.append("--Mapper.tri_ignore_two_view_tracks 0")
        self.run(" ".join(args))

        args = ["colmap model_converter"]
        args.append(f"--input_path {os.path.join(self.sparse_path, '0')}")
        args.append(f"--output_type PLY")
        args.append(f"--output_path {os.path.join(self.ws_path, 'sparse_0.ply')}")
        self.run(" ".join(args))

    def feature_extractor(self, use_gpu=1):
        """
        colmap feature_extractor
          --database_path arg
          --image_path arg
          --camera_mode arg (=-1)
          --ImageReader.mask_path arg
        """
        args = ["colmap feature_extractor"]
        args.append("--SiftExtraction.use_gpu {use_gpu}")
        args.append(f"--database_path {self.database_path}")
        args.append(f"--image_path {self.image_path}")
        if self.mask_path is not None:
            args.append(f"--ImageReader.mask_path {self.mask_path}")
        args.append(f"--camera_mode {CameraMode.PER_FOLDER.value}")
        self.run(" ".join(args))

    def exhaustive_matcher(self):
        args = [f"colmap exhaustive_matcher"]
        args.append(f"--database_path {self.database_path}")
        self.run(" ".join(args))


@command
def reconstruct(ws_path, image_path, data_type="video", quality="medium", dense=1, mask_path=None):
    col = Colmap(ws_path)
    col.set_images(image_path)
    col.set_mask_images(mask_path)
    col.automatic_reconstructor(data_type, quality, dense=dense)

@command
def my_reconstruct(ws_path, image_path, data_type="video", quality="medium", mask_path=None):
    col = Colmap(ws_path)
    col.set_images(image_path)
    col.set_mask_images(mask_path)
    col.my_reconstructor(data_type, quality)

@command
def feature_extraction(ws_path, image_path, mask_path=None):
    col = Colmap(ws_path)
    col.set_images(image_path)
    col.set_mask_images(mask_path)
    col.feature_extractor()

@command
def run_command(ws_path, commands):
    print(f"{ws_path} {commands}")
    col = Colmap(ws_path)
    col.run(commands)

if __name__ == "__main__":
    # logger from config file
    config.fileConfig(os.path.join(os.path.dirname(__file__), 'logconf.ini'))
    logger = getLogger(__name__)

    # run command
    Run()
