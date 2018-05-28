import logging
import os
import time


def init_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    file_handler = logging.FileHandler('Logs/' + time.strftime("%b-%d-%Y-%H:%M:%S-")
                                       + name + '-test.log')
    formatter = logging.Formatter('%(asctime)s %(name)s[line:%(lineno)d]'
                                  '%(levelname)s %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# logger = init_logger('logger')
# logger.info('it is info')
# logger.warning('it is warn')
# logger.error('it is error')
# logger.fatal('it is fatal')
# logger.critical('it is critical')
