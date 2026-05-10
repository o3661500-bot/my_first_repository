import logging
from module_2 import devide_number
from module_3 import square_number

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

class ErroeLogFiltr(logging.Filter):
    def filter(self, record):
        return record.levelname == "ERROR"

formatter_1 = logging.Formatter(
    fmt='[{asctime}] #{levelname:8} {filename}:'
    '{lineno} - {name}:{funcName} - {message}',
    style='{'
)

error_file = logging.FileHandler('error.log', 'w', encoding='utf-8')

error_file.setLevel(logging.DEBUG)

error_file.addFilter(ErroeLogFiltr())

error_file.setFormatter(formatter_1)

logger.addHandler(error_file)

def main():
    a, b = 12, 2
    c, d = 4, 0

    logger.debug("Лог DEBUG")
    logger.info("Log INFO")
    logger.warning("Log WARNING")
    logger.error("Log ERROR")
    logger.critical("Log CRITICAL")

    print(devide_number(a, square_number(b)))
    print(devide_number(square_number(c), d))