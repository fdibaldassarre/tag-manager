#!/usr/bin/env python3

import logging
from logging.handlers import RotatingFileHandler
import os

from src.Config import ConfigManager


class Logger():
    formatter = logging.Formatter(
        fmt="%(asctime)-22s %(levelname)-7s %(name)-14s :: %(funcName)s == %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logpath = None
    file_handler = None
    stream_handler = None
    loggers = []

    def __init__(self):
        self._createStreamHandler()

    def hasFileWriter(self):
        return self.file_handler is not None

    def _createFileHandler(self):
        self.file_handler = RotatingFileHandler(self.logpath,
                                                maxBytes=1048576,
                                                backupCount=10)
        self.file_handler.setFormatter(self.formatter)

    def _createStreamHandler(self):
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.formatter)

    def setLogPath(self, path):
        self.logpath = path
        self._createFileHandler()
        self.addFileHandlerToAll()

    def getFileHandler(self):
        return self.file_handler

    def getStreamHandler(self):
        return self.stream_handler

    def addLogger(self, logger):
        self.loggers.append(logger)
        self.addFileHandler(logger)
        if ConfigManager.debug:
            self.addStreamHandler(logger)
            logger.setLevel(logging.DEBUG)

    def addFileHandler(self, logger):
        if self.file_handler is not None:
            logger.addHandler(self.file_handler)

    def addStreamHandler(self, logger):
        logger.addHandler(self.stream_handler)

    def addFileHandlerToAll(self):
        for logger in self.loggers:
            self.addFileHandler(logger)


# Create the logger singleton
mainLogger = Logger()

def _initializeFileWriter():
    '''
        Initialize the main logger file writer
    '''
    log_folder = os.path.join(ConfigManager.profile_folder, "logs/")
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)
    path = os.path.join(log_folder, "main.log")
    mainLogger.setLogPath(path)
    return mainLogger

def _setupLogger(logger):
    '''
        Add all the necessary handlers and set the level of the given
        logger.

        :param Logger logger: Logger
    '''
    logger.setLevel(logging.INFO)
    if not mainLogger.hasFileWriter():
        _initializeFileWriter()
    mainLogger.addLogger(logger)


def createLogger(name):
    '''
        Create and setup a logger with the given name.

        :param str name: Name of the logger
        :return: A logger
        :rtype: Logger
    '''
    logger = logging.getLogger(name)
    _setupLogger(logger)
    return logger
