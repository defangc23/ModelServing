#!/usr/bin/python
# coding=utf-8

import os, sys
import logging
from logging.handlers import RotatingFileHandler


LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'notset': logging.NOTSET,
}


def get_logger(log_file_name, max_bytes=50 * 1024 * 1024, backup_cnt=10, level='debug'):
    logger = logging.getLogger(log_file_name)
    logger.setLevel(LOG_LEVELS[level])
    log_dir = './log/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = log_dir + log_file_name + '.log'
    file_handler = RotatingFileHandler(log_path,
                                       mode='a',
                                       maxBytes=max_bytes,
                                       backupCount=backup_cnt,
                                       encoding='utf8')

    # Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level=logging.DEBUG)
    logger.addHandler(stream_handler)

    # define log format, e.g.
    # 2018-10-08 18:21:58,071 - test.py[line:31] - INFO - info message
    formatter = logging.Formatter(
        '%(asctime)s | %(filename)s[line:%(lineno)d]-%(levelname)s-[pid:%(process)d]: %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
