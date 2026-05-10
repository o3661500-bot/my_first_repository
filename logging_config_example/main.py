import logging
from module_1 import main

logging.basicConfig(
    format='#{levelname:8} {name}:{funcName} - {message}',
    style='{'
)

main()