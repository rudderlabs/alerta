from enum import Enum
import json
import logging
import os
from rudder_enrichment.environment import PLUGIN_DIR, DITTO_JSON_PATH


class ProjectIdentifier(Enum):
    NOTIFICATIONS_AND_ALERTS = 'project_630f9ed947a50a5d161c8b30'


projectwise_data = {}
DEFAULT_PROJECT = ProjectIdentifier.NOTIFICATIONS_AND_ALERTS

def get_all_data():
    global projectwise_data

    if len(projectwise_data) == 0:
        try:
            with open(DITTO_JSON_PATH, 'r') as f:
                projectwise_data = json.load(f)['projects']
        except Exception as e:
            logging.error(f"Ditto: Error loading data; {e}", exc_info=True)

    return projectwise_data


def get_project_data(project: ProjectIdentifier = None):
    data = {}

    try:
        data = get_all_data()[DEFAULT_PROJECT.value if project is None else project.value]
    except Exception as e:
        logging.error(f"Ditto: Error loading {project.name} data; {e}", exc_info=True)

    return data
