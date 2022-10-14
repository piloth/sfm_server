# std. library
import sys
import os
import unittest
from logging import config, getLogger

# third party
from commandr import command, Run

# modules
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from modules.SSHRunner import SSHRunner


class TestSSHRunnerMethods(unittest.TestCase):

    def test_run(self):
        ssh = SSHRunner()
        ssh.connect(hostname="colmap", port=20022, username="root", key_filename="/root/.ssh/id_rsa")
        ret = ssh.run("ls -l")
        self.assertEqual(ret, 0)

    def test_failure(self):
        ssh = SSHRunner()
        ssh.connect(hostname="colmap", port=20022, username="root", key_filename="/root/.ssh/id_rsa")
        ret = ssh.run("exit 12")
        self.assertEqual(ret, 12)


if __name__ == "__main__":
    unittest.main()
