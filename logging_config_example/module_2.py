import logging
import sys

logger = logging.getLogger(__name__)

class DebugWarningFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in ('DEBUG', "WARNING")

formatter_2 = logging.Formatter(
    fmt='#{levelname:8} [{asctime}] - {filename}:'
    '{lineno} - {name}:{funcName} - {message}',
    style="{"
)

stdout = logging.StreamHandler(sys.stdout)

stdout.addFilter(DebugWarningFilter())

stdout.setFormatter(formatter_2)

logger.addHandler(stdout)

def devide_number(dividend: int | float, devider: int | float):

    logger.debug("log DEBUG")
    logger.info("log INFO")
    logger.warning("log WARNING")
    logger.error("log ERROR")
    logger.critical("log CRITICAL")

    try:
        return dividend / devider
    except:
        logger.exception('Произошло деление на 0')