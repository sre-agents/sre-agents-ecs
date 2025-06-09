import sys

from loguru import logger


def filter_log():
    import logging
    import warnings

    from urllib3.exceptions import InsecureRequestWarning

    # ignore all warnings
    warnings.filterwarnings("ignore")

    # ignore UserWarning
    warnings.filterwarnings(
        "ignore", category=UserWarning, module="opensearchpy.connection.http_urllib3"
    )

    # ignore InsecureRequestWarning
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)

    # disable logs
    logging.basicConfig(level=logging.ERROR)


def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{file}:{line}</cyan> - {message}",
        colorize=True,
        level="DEBUG",
    )
    return logger


filter_log()
setup_logger()


def get_logger(name: str):
    return logger.bind(name=name)
