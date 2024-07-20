import os
import sys
import socket
import logging
import logging.handlers
from .config import Config

# Logging 포맷 설정
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


class SysLog:
    def __init__(self, alias=None, devel=False):
        self.home = os.getenv('ATHENA_HOME')
        self.alias = alias
        self.devel = devel

    def create_logger(self) -> logging.Logger:
        if not self.devel:
            config = Config('athena-agent.yaml')
            level = self._get_log_level(config.get_value('log/level'))
            count = self._get_log_count(config.get_value('log/rotate'))
            size = self._get_log_bytes(config.get_value('log/size'))
            name = self._get_log_name()

            logger = logging.getLogger('athena-worker')
            logger.setLevel(level)
            file_handler = logging.handlers.RotatingFileHandler(filename=name, maxBytes=size, backupCount=count)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            stdout_handler = logging.StreamHandler(sys.stdout)
            logger.addHandler(stdout_handler)
        return logger

    def _get_log_level(self, level_str):
        if level_str == 'info':
            level = logging.INFO
        elif level_str == 'warn':
            level = logging.WARNING
        elif level_str == 'error':
            level = logging.ERROR
        else:
            level = logging.DEBUG
        return level

    def _get_log_count(self, rotate_str):
        return int(rotate_str)

    def _get_log_bytes(self, size_str):
        i = size_str.find('kb')
        if i > 0:
            return int(size_str[:i]) * 1024
        i = size_str.find('mb')
        if i > 0:
            return int(size_str[:i]) * 1024 * 1024
        i = size_str.find('gb')
        if i > 0:
            return int(size_str[:i]) * 1024 * 1024 * 1024
        return 0

    def _get_log_path(self, dir_str):
        return os.path.join(self.home, 'logs', dir_str)

    def _get_log_name(self):
        path = os.path.join(self.home, 'logs', 'agent')
        file = self.alias + '@' + socket.gethostname() + '.log'
        return os.path.join(path, file)


