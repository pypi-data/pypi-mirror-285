import logging
import enum

# Create a logger object
logger = logging.getLogger('toolshop')
handler = logging.StreamHandler()
logger.addHandler(handler)


class LoggingPreset(enum.Enum):
    """Enum for logging presets"""
    MINIMAL_VERBOSE = 'minimal_verbose'
    CLASSIC_VERBOSE = 'classic_verbose'
    MINIMAL = 'minimal'


def configure_logging(preset=None, level=None, format=None):
    """Configure toolshop's log level and log format"""
    if preset:
        if preset == LoggingPreset.MINIMAL_VERBOSE:
            level = logging.INFO
            format = '%(message)s'
        elif preset == LoggingPreset.CLASSIC_VERBOSE:
            level = logging.INFO
            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        elif preset == LoggingPreset.MINIMAL:
            level = logging.WARNING
            format = '%(message)s'
    
    logger.setLevel(level)
    for h in logger.handlers:
        if level:
            h.setLevel(level)
        if format:
            h.setFormatter(logging.Formatter(format))


# Set toolshop's default logging configuration
configure_logging(preset=LoggingPreset.MINIMAL)
