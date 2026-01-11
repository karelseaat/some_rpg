import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_file="somerpg.log"):
    """Configure and return the application logger."""
    
    # Create a custom logger
    logger = logging.getLogger("somerpg")
    logger.setLevel(logging.INFO)
    
    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)
    
    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    
    # Add handlers to the logger
    # Avoid adding handlers multiple times if setup is called twice
    if not logger.handlers:
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
    
    return logger

# Initialize default logger instance
logger = setup_logging()
