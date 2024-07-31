import os

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0

RUDDER_CONFIG_BACKEND_SERVICE_BASE_URL = os.environ.get('RUDDER_CONFIG_BACKEND_SERVICE_BASE_URL') or app.config[
    'RUDDER_CONFIG_BACKEND_SERVICE_BASE_URL']
RUDDER_CONFIG_BACKEND_ADMIN_USERNAME = os.environ.get('RUDDER_CONFIG_BACKEND_ADMIN_USERNAME') or app.config[
    'RUDDER_CONFIG_BACKEND_ADMIN_USERNAME']
RUDDER_CONFIG_BACKEND_ADMIN_PASSWORD = os.environ.get('RUDDER_CONFIG_BACKEND_ADMIN_PASSWORD') or app.config[
    'RUDDER_CONFIG_BACKEND_ADMIN_PASSWORD']
RUDDER_CONFIG_BACKEND_DATA_CACHE_TTL = int(
    os.environ.get('RUDDER_CONFIG_BACKEND_DATA_CACHE_TTL') or app.config['RUDDER_CONFIG_BACKEND_DATA_CACHE_TTL'])
RUDDER_CONFIG_BACKEND_CACHE_STORE_MAX_SIZE = int(
    os.environ.get('RUDDER_CONFIG_BACKEND_CACHE_STORE_MAX_SIZE') or app.config[
        'RUDDER_CONFIG_BACKEND_CACHE_STORE_MAX_SIZE']
)
"""
TODO: Pick the URL based on different "Environment" from which the alert is generated from.
"""
RUDDER_WEB_APP_URL_PREFIX = os.environ.get('RUDDER_WEB_APP_URL_PREFIX') or app.config['RUDDER_WEB_APP_URL_PREFIX']
PLUGIN_DIR = 'rudder-alerta-enrichment-plugin'
DITTO_JSON_PATH = os.environ.get('DITTO_JSON_PATH') or app.config['DITTO_JSON_PATH']
ALERT_METADATA_CONFIG_FILE = os.environ.get('ALERT_METADATA_CONFIG_FILE') or app.config['ALERT_METADATA_CONFIG_FILE']
