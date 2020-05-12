import logging

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


def get_logger():
    return logger
