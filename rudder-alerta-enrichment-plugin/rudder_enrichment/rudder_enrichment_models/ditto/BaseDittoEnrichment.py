from abc import ABC, abstractmethod
import datetime
import json
import logging
import re

from rudder_enrichment.environment import RUDDER_WEB_APP_URL_PREFIX
from rudder_enrichment.rudder_enrichment_models.ditto import projects
from rudder_enrichment.rudder_enrichment_models import utils


class BaseDittoEnrichment(ABC):
    FRAME_NAME = 'frame_SES_Alert'
    BLOCK_NAME = 'amazon-ses-template'

    @abstractmethod
    def __init__(self, alert_type, ditto_variant_base_name, workspace_id, url, severity, workspace_metadata, raw_data):
        self.alert_type = alert_type

        if severity == 'normal':
            self.ditto_variant_name = ditto_variant_base_name + '_normal'
            raise Exception("Normal state variant not supported")
        else:
            self.ditto_variant_name = ditto_variant_base_name

        self.workspace_id = workspace_id
        self.url = url
        self.severity = severity
        self.workspace_metadata = workspace_metadata
        self.var_values_map = None
        self.raw_data = raw_data

    def build_var_values_map(self, **kwargs):
        customer_name = None

        try:
            customer_name = self.workspace_metadata.company_name
        except Exception:
            pass

        if customer_name is None:
            customer_name = ''

        var_values_map = {'customer': customer_name, 'workspace_id': self.workspace_id,
                          'cp_base_url': RUDDER_WEB_APP_URL_PREFIX, 'severity': self.severity}
        var_values_map.update(self.extract_metadata_from_raw_data())
        var_values_map.update(kwargs)

        return var_values_map

    def extract_metadata_from_raw_data(self):
        metadata = {}
        try:
            if self.raw_data is not None:
                raw_json = json.loads(self.raw_data)
                if 'series' in raw_json:
                    series = raw_json['series'][0]

                    if 'columns' in series and 'values' in series:
                        columns = series['columns']
                        values = series['values'][0]
                        pattern = "m.*[.]"
                        for (column, value) in zip(columns, values):
                            # Normalizing column for kapacitor multi-metric-template
                            normalized_column = re.sub(pattern, '', column)

                            metadata[normalized_column] = value

                    if 'tags' in series:
                        metadata.update(series['tags'])

                if 'labels' in raw_json:
                    metadata.update(raw_json['labels'])

        except Exception as e:
            logging.error(f"DittoRudderEnrichment: error extracting metadata {e}", exc_info=True)
        return metadata


    def build_alert_metadata_map(self, **kwargs):
        alert_metadata_map = {
            'workspace_id': self.workspace_id,
            'workspace_name': self.workspace_metadata.name,
            'organization_name': self.workspace_metadata.organization.get('name'),
            'organization_id': self.workspace_metadata.organization.get('id'),
            'namespace': self.get_namespace(),
            'plan': self.workspace_metadata.organization.get('billingInfo', {}).get('planName'),
            'alert_name':self.alert_type
        }
        alert_metadata_map.update(kwargs)

        return alert_metadata_map


    def get_namespace(self):
        namespace = ''

        if self.raw_data is None:
            return namespace

        raw_json = json.loads(self.raw_data)

        is_namespace_in_kapacitor_payload = len(raw_json.get('series', [])) > 0 and raw_json.get('series')[0].get('tags', {}).get('namespace')
        is_namespace_in_prometheus_payload = raw_json.get('labels', {}).get('namespace')
        if is_namespace_in_kapacitor_payload:
            namespace = raw_json.get('series')[0].get('tags', {}).get('namespace')
        elif is_namespace_in_prometheus_payload:
            namespace = raw_json.get('labels', {}).get('namespace')

        return namespace


    def get_target_name(self):
        pass

    def substitute_vars_in_text(self, text: str, ditto_vars_map: dict, var_values_map: dict):
        if len(ditto_vars_map) == 0:
            return text

        for ditto_var, ditto_values in ditto_vars_map.items():
            if 'Text' in ditto_values and 'URL' in ditto_values:
                piece = f'<a href="{ditto_values["URL"]}" target="_blank">{ditto_values["Text"]}</a>'
            else:
                piece = var_values_map.get(ditto_var)

                if piece is None:
                    logging.error(f'DittoRudderEnrichment error: Cannot find value for {ditto_var} for text {text}.')
                    piece = ditto_vars_map.get(ditto_var, {}).get('Fallback')

            if piece is not None:
                text = re.sub('{{' + ditto_var + '}}', str(piece), text)
            else:
                logging.error(f'DittoRudderEnrichment error: Cannot find fallback value for {ditto_var} for text {text}.')

        return text

    def fetch_component_with_substitutions_and_overrides(self, block: dict, component: str, var_values_map: dict):
        text = block[component].get('text')
        ditto_vars_map = block[component].get('variables', {})
        override = block[component].get('variants', {}).get(self.ditto_variant_name, {}).get('text')

        if override is not None:
            text = override
            ditto_vars_map.update(block[component].get('variants', {}).get(self.ditto_variant_name, {}).get('variables', {}))

        return self.substitute_vars_in_text(text, ditto_vars_map, var_values_map)

    def enrich(self):
        incident_time = datetime.datetime.utcnow().strftime("%d-%b-%y %H:%M")
        var_values_map = self.build_var_values_map(incident_time=incident_time)
        block = projects.get_project_data()['frames'][self.__class__.FRAME_NAME]['otherText']

        greeting = self.fetch_component_with_substitutions_and_overrides(block, 'greeting', var_values_map)
        email_subject = self.fetch_component_with_substitutions_and_overrides(block, 'subject', var_values_map)
        button_name = self.fetch_component_with_substitutions_and_overrides(block, 'cta_button_text', var_values_map)
        button_url = self.fetch_component_with_substitutions_and_overrides(block, 'cta_button_link', var_values_map)
        button_url = utils.add_query_params_to_url(button_url, {})
        body = self.fetch_component_with_substitutions_and_overrides(block, 'body', var_values_map)
        email_body_heading = self.fetch_component_with_substitutions_and_overrides(block, 'body_heading', var_values_map)
        signature = self.fetch_component_with_substitutions_and_overrides(block, 'signature', var_values_map)
        notification_settings_text = self.fetch_component_with_substitutions_and_overrides(block, 'manage_alerts', var_values_map)
        notification_settings_url = self.fetch_component_with_substitutions_and_overrides(block, 'manage_alerts_link', var_values_map)
        notification_settings_url = utils.add_query_params_to_url(notification_settings_url, {})

        email_body = f"""
        {greeting}<br/><br/>
        {body}
        <br/><br/>
        {signature}
        """

        return {
            'title': email_subject,
            'body': email_body,
            'email_button_url': button_url,
            'email_body_heading': email_body_heading,
            'button_name': button_name,
            'notification_settings_text': notification_settings_text,
            'notification_settings_url': notification_settings_url,
            'metadata': self.build_alert_metadata_map()
        }