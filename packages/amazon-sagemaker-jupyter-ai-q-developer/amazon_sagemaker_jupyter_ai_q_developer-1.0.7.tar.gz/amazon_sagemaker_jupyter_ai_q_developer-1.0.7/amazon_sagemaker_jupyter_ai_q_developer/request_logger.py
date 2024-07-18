
import logging
import os

from amazon_sagemaker_jupyter_ai_q_developer.constants import LOGGER_NAME, LOG_FILE_NAME, LOG_FILE_PATH, METRICS_NAMESPACE
from aws_embedded_metrics.logger.metrics_context import MetricsContext
from aws_embedded_metrics.serializers.log_serializer import LogSerializer

def init_api_operation_logger(server_log):
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_file_location = os.path.join(LOG_FILE_PATH, LOG_FILE_NAME)

    try:
        os.makedirs(LOG_FILE_PATH, exist_ok=True)
        log_file_location = os.path.join(LOG_FILE_PATH, LOG_FILE_NAME)
        file_handler = logging.FileHandler(log_file_location)
        logger.addHandler(file_handler)
        server_log.info(f"Q Dev Chat API Logger Initialized and logs in - {log_file_location},{LOGGER_NAME}")
    except Exception as ex:
        server_log.info(f"Unable to create log file directory - {LOG_FILE_PATH}, {ex}, using StreamHandler")
        logger.addHandler(logging.StreamHandler())

def get_new_metrics_context(operation):
    context = MetricsContext().empty()
    context.namespace = METRICS_NAMESPACE
    context.should_use_default_dimensions = False
    context.put_dimensions({"Operation" : operation})
    return context

def flush_metrics(ctx):
    logger = logging.getLogger(LOGGER_NAME)
    for serialized_content in LogSerializer.serialize(ctx):
        if serialized_content:
            logger.info(serialized_content)
