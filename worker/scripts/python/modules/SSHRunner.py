# std. library
import sys
import os
from logging import getLogger, NullHandler, DEBUG

# third party
import paramiko
from itertools import zip_longest


class SSHRunner(paramiko.SSHClient):
    def __init__(self):
        super().__init__()
        self.logger = getLogger(__name__)
        #self.logger.propagate = True
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    def run(self, command):
        self.logger.info(command)
        cwd = os.getcwd()
        channel = self.get_transport().open_session()
        channel.set_combine_stderr(True)
        stdout = channel.makefile()
        try:
            channel.exec_command(f"cd {cwd}; {command}")
            self.logger.info("called")
            for out in stdout:
                if out: self.logger.info(out.strip())
            return_code = stdout.channel.recv_exit_status()
            return return_code
        finally:
            channel.close()
