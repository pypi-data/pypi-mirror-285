import logging
import logging.handlers

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info("DHuO Lib - Configured Logging")
