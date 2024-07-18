import logging
import logging.config
import pkg_resources
import yaml


stream_config = pkg_resources.resource_stream(__name__, 'config/logs.yaml')
config = yaml.safe_load(stream_config.read())
logging.config.dictConfig(config=config)


logger = logging.getLogger(__name__)
