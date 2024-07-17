import logging
import yaml


def get_logger(name='cli', level=logging.DEBUG):
    """
    Get a logger instance with the specified name and log level.

    Args:
        name (str, optional): The name of the logger. Defaults to 'cli'.
        level (int, optional): The log level for the logger. Defaults to logging.DEBUG.

    Returns:
        logging.Logger: The logger instance.

    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # log level for handler
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.propagate = False
    return logger


logger = get_logger()


def parse_yaml(filepath: str):
    """
    Parses a YAML file and returns the parsed content.

    Args:
        filepath (str): The path to the YAML file.

    Returns:
        dict: The parsed content of the YAML file.

    """
    parsed = None
    try:
        with open(filepath) as f:
            content = f.read()
        parsed = yaml.safe_load(content)
        parsed['_full_content'] = content
    except Exception as e:
        logger.exception('parse yaml error')
    return parsed
