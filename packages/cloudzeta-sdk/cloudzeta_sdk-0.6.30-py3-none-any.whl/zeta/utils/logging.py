import logging
import sys

# Set up logging
zetaLogger = logging.getLogger("zeta")
zetaLogger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s %(message)s')
stdout_handler.setFormatter(formatter)
zetaLogger.addHandler(stdout_handler)
