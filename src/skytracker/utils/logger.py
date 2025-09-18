"""Package logging utilities"""
import logging
from typing import Optional, Any
import sys
import os
from pathlib import Path


LOG_FORMAT: str = '%(asctime)s [%(levelname)s] %(relativepath)s - %(message)s'


class PackagePathFilter(logging.Filter):
    """Filter to get relative module path"""

    def filter(self, record: logging.LogRecord) -> Any:
        """Process a logging record

        Args:
            record (logging.LogRecord): logging record

        Returns:
            Any: result
        """
        pathname = record.pathname
        record.relativepath = None
        abs_sys_path = map(os.path.abspath, sys.path)
        for path in sorted(abs_sys_path, key=len, reverse=True):
            if not path.endswith(os.sep):
                path += os.sep
            if pathname.startswith(path):
                record.relativepath = os.path.relpath(pathname, path)
                break
        return True


def setup_logger(name: Optional[str] = None, level: int = logging.INFO,
                 log_file: Optional[str] = None) -> logging.Logger:
    """Configure a logger for the application

    Args:
        name (str, optional): logger name (root if not specified). Defaults to None.
        level (int, optional): logging level. Defaults to logging.INFO.
        log_file (str, optional): path to file to log in. Defaults to ".\\logs\\skytracker.log".

    Returns:
        logging.Logger: configured logger
    """
    # Parse log file argument
    if log_file is None:
        log_file: Path = Path('.', 'logs', 'skytracker.log')
    else:
        log_file: Path = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Get logger (return if already configured)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    # Set log level
    logger.setLevel(level)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    console_handler.addFilter(PackagePathFilter())
    logger.addHandler(console_handler)

    # Add file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler.addFilter(PackagePathFilter())
    logger.addHandler(file_handler)

    return logger

logger: logging.Logger = setup_logger('skytracker')
