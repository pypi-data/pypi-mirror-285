import json
import logging.config
import os
import pathlib

this_dir = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

logging_config_path = this_dir / "resources/logging.json"

with open(logging_config_path, "r") as f:
    LOGGING_CONFIG = json.load(f)

logging.config.dictConfig(LOGGING_CONFIG)

log = logging.getLogger(__name__)
log.debug("Logging is configured.")
