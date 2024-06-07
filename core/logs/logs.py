import logging
import sys


def setup_logger(logger_name, log_file, level=logging.INFO):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Создание обработчика для сохранения логов в файл
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Создание обработчика для вывода логов в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger_error = setup_logger("error_logger", "core/logs/error_logs.log")

logger_response = setup_logger("response_logger", "core/logs/response_logs.log")
