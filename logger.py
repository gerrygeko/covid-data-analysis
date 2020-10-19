import logging


WERKZEUG_LOG_LEVEL = logging.ERROR


def initialize_logger():
    fh = logging.FileHandler('complete.log')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        handlers=[fh, ch])
    logger = logging.getLogger('dash_app')
    logger.setLevel(logging.INFO)
    logger.addHandler(fh)
    change_werkzeug_log_level(WERKZEUG_LOG_LEVEL)
    logger.info(f"Changed werkzeug log level to {logging.getLevelName(WERKZEUG_LOG_LEVEL)}")


def change_werkzeug_log_level(log_level):
    log = logging.getLogger('werkzeug')
    log.setLevel(log_level)


def get_logger():
    logger = logging.getLogger('dash_app')
    return logger
