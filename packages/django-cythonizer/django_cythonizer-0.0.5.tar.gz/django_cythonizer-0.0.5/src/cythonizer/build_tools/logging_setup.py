import os
import logging
from datetime import datetime
from .config import LOG_DIR
from .config import  LOG_FILENAME

def setup_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, LOG_FILENAME.format(timestamp=timestamp))
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    logger = logging.getLogger('build_logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.propagate = False
    
    return logger

logger = setup_logging()