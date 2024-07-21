import logging
import os


def genFormatter(color: bool = False) -> logging.Formatter:
    clr = {
        'red': '\x1b[91m',
        'gre': '\x1b[92m',
        'yel': '\x1b[93m',
        'blu': '\x1b[94m',
        'mag': '\x1b[95m',
        'cyn': '\x1b[96m',
        'rst': '\x1b[0m'
    }
    logfmtstr = f'[{clr["mag"]}%(asctime)s{clr["rst"]}]'
    logfmtstr += f' [{clr["yel"]}%(filename)s{clr["rst"]}'
    logfmtstr += f':{clr["cyn"]}%(lineno)s{clr["rst"]}]'
    logfmtstr += f' [{clr["red"]}%(name)s{clr["rst"]}]'
    logfmtstr += f' [{clr["blu"]}%(levelname)s{clr["rst"]}]'
    logfmtstr += ': %(message)s'
    if not color:
        for esc in clr.values():
            logfmtstr = logfmtstr.replace(esc, '')
    return logging.Formatter(logfmtstr)


def getLoggerFile() -> str:
    user = os.getenv('USER')
    loggerFile = f'/tmp/{user}.owega.log'
    return loggerFile


def getLogger(name, debug: bool = False) -> logging.Logger:
    # user = os.getenv('USER')
    loggerFile = getLoggerFile()
    logger = logging.getLogger(name)

    consHand = logging.StreamHandler()
    if debug:
        consHand.setLevel(logging.DEBUG)
    else:
        consHand.setLevel(logging.WARNING)
    consHand.setFormatter(genFormatter(color=True))
    logger.addHandler(consHand)

    fileHand = logging.FileHandler(loggerFile)
    fileHand.setLevel(logging.DEBUG)
    fileHand.setFormatter(genFormatter(color=False))
    logger.addHandler(fileHand)

    return logger
