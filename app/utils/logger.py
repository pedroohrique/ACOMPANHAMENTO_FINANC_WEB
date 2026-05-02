import logging
import os

def log_builder(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # Usando caminho relativo para o arquivo de log
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(log_dir, "log_aplicacao.txt")
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG) 
    formatter = logging.Formatter('%(asctime)s / %(levelname)s / %(name)s / %(funcName)s / %(message)s / line: %(lineno)d')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger