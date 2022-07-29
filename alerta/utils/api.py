import logging
import os
import threading
from functools import wraps
from typing import Optional, Tuple

from flask import current_app, g

from alerta.app import plugins
from alerta.exceptions import (AlertaException, ApiError, ForwardingLoop, InvalidAction, RejectException)
from alerta.models.alert import Alert
from alerta.models.enums import Scope
from alerta.stats import StatsD
from alerta.utils.rule_processor import process_forward_rules_for_alert
from alerta.exceptions import (AlertaException, ApiError, BlackoutPeriod,
                               ForwardingLoop, HeartbeatReceived,
                               InvalidAction, RateLimit, RejectException)


def assign_customer(wanted: str = None, permission: Scope = Scope.admin_alerts) -> Optional[str]:
    customers = g.get('customers', [])
    if wanted:
        if Scope.admin in g.scopes or permission in g.scopes:
            return wanted
        if wanted not in customers:
            raise ApiError(f"not allowed to set customer to '{wanted}'", 400)
        else:
            return wanted
    if customers:
        if len(customers) > 1:
            raise ApiError('must define customer as more than one possibility', 400)
        else:
            return customers[0]
    return None


def process_alert(alert: Alert) -> Alert:
    try:
        is_duplicate = alert.is_duplicate()
        if is_duplicate:
            alert = alert.deduplicate(is_duplicate)
        else:
            is_correlated = alert.is_correlated()
            if is_correlated:
                alert = alert.update(is_correlated)
            else:
                alert = alert.create()
    except Exception as e:
        raise ApiError(str(e))
    return alert


def process_action(alert: Alert, action: str, text: str, timeout: int = None) -> Tuple[Alert, str, str, Optional[int]]:
    wanted_plugins, wanted_config = plugins.routing(alert)

    updated = None
    for plugin in wanted_plugins:
        if alert.is_suppressed:
            break
        try:
            updated = plugin.take_action(alert, action, text, timeout=timeout, config=wanted_config)
        except NotImplementedError:
            pass  # plugin does not support action() method
        except (RejectException, ForwardingLoop, InvalidAction, AlertaException):
            raise
        except Exception as e:
            if current_app.config['PLUGINS_RAISE_ON_ERROR']:
                raise ApiError(f"Error while running action plugin '{plugin.name}': {str(e)}")
            else:
                logging.error(f"Error while running action plugin '{plugin.name}': {str(e)}")

        if isinstance(updated, Alert):
            updated = updated, action, text, timeout
        if isinstance(updated, tuple):
            if len(updated) == 4:
                alert, action, text, timeout = updated
            elif len(updated) == 3:
                alert, action, text = updated

    if updated:
        alert.update_tags(alert.tags)
        alert.attributes = alert.update_attributes(alert.attributes)

    return alert, action, text, timeout


def process_note(alert: Alert, text: str) -> Tuple[Alert, str]:
    wanted_plugins, wanted_config = plugins.routing(alert)

    updated = None
    for plugin in wanted_plugins:
        try:
            updated = plugin.take_note(alert, text, config=wanted_config)
        except NotImplementedError:
            pass  # plugin does not support take_note() method
        except (RejectException, ForwardingLoop, AlertaException):
            raise
        except Exception as e:
            if current_app.config['PLUGINS_RAISE_ON_ERROR']:
                raise ApiError(f"Error while running note plugin '{plugin.name}': {str(e)}")
            else:
                logging.error(f"Error while running note plugin '{plugin.name}': {str(e)}")

        if isinstance(updated, Alert):
            updated = updated, text
        if isinstance(updated, tuple) and len(updated) == 2:
            alert, text = updated

    if updated:
        alert.update_tags(alert.tags)
        alert.update_attributes(alert.attributes)

    return alert, text


def process_status(alert: Alert, status: str, text: str) -> Tuple[Alert, str, str]:
    wanted_plugins, wanted_config = plugins.routing(alert)

    updated = None
    for plugin in wanted_plugins:
        if alert.is_suppressed:
            break
        try:
            updated = plugin.status_change(alert, status, text, config=wanted_config)
        except TypeError:
            updated = plugin.status_change(alert, status, text)  # for backward compatibility
        except (RejectException, AlertaException):
            raise
        except Exception as e:
            if current_app.config['PLUGINS_RAISE_ON_ERROR']:
                raise ApiError(f"Error while running status plugin '{plugin.name}': {str(e)}")
            else:
                logging.error(f"Error while running status plugin '{plugin.name}': {str(e)}")
        if updated:
            try:
                alert, status, text = updated
            except Exception:
                alert = updated

    if updated:
        alert.update_tags(alert.tags)
        alert.attributes = alert.update_attributes(alert.attributes)

    return alert, status, text


def process_delete(alert: Alert) -> bool:
    wanted_plugins, wanted_config = plugins.routing(alert)

    delete = True
    for plugin in wanted_plugins:
        try:
            delete = delete and plugin.delete(alert, config=wanted_config)
        except NotImplementedError:
            pass  # plugin does not support delete() method
        except (RejectException, AlertaException):
            raise
        except Exception as e:
            if current_app.config['PLUGINS_RAISE_ON_ERROR']:
                raise ApiError(f"Error while running delete plugin '{plugin.name}': {str(e)}")
            else:
                logging.error(f"Error while running delete plugin '{plugin.name}': {str(e)}")

    return delete and alert.delete()
