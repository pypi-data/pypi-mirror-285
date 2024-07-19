import logging


def init_log():
    # create logger
    logger = logging.getLogger('PYT')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter("%(asctime)s [%(name)s] \033[36m%(levelname)s\033[0m [%(filename)s:%(lineno)d] \033[36m%(message)s\033[0m", datefmt='%Y-%m-%d %H:%M:%S')
        
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger
