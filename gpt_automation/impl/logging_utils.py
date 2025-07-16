import logging
import os

def get_logger(name: str, log_file: str = None):
    """
    Returns a logger with a file handler (DEBUG/INFO) and a console handler (WARNING).
    If log_file is not provided, logs only to console (WARNING+).
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if getattr(logger, '_centralized', False):
        return logger  # Already configured

    # Remove all handlers first
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler (WARNING+)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
    logger.addHandler(ch)

    # File handler (if log_file specified)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        logger.addHandler(fh)

    logger._centralized = True
    return logger

def close_logger_handlers(name: str):
    """
    Closes and removes all handlers for the given logger name.
    Useful for test cleanup to release log files.
    """
    logger = logging.getLogger(name)
    for handler in logger.handlers[:]:
        try:
            handler.close()
        except Exception as e:
            print(f"Error closing handler {handler}: {e}")
        logger.removeHandler(handler)
    # Ensure all logging resources are released (important for Windows file locks)
    logging.shutdown()
