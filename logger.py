import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('complete.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)


def get_logger():
    return logger
