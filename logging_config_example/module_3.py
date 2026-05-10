import logging

logger = logging.getLogger(__name__)

class CriticalFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == "CRITICAL"

formatter_3 = logging.Formatter(
    fmt="#{levelname:8} [{asctime}] - {message}",
    style="{"
)

stderr = logging.StreamHandler()

critical_file = logging.FileHandler("critical.log", mode="w", encoding='utf-8')

critical_file.setFormatter(formatter_3)

critical_file.addFilter(CriticalFilter())

logger.addHandler(stderr)
logger.addHandler(critical_file)

def square_number(number: int | float):

    logger.debug('Лог DEBUG')
    logger.info('Лог INFO')
    logger.warning('Лог WARNING')
    logger.error('Лог ERROR')
    logger.critical('Лог CRITICAL')

    return number ** 2
