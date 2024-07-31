import datetime
import logging
import urllib.parse as urlparse
from urllib.parse import urlencode

from rudder_enrichment.config_backend_client import ConfigBackendClient
from rudder_enrichment.environment import RUDDER_CONFIG_BACKEND_SERVICE_BASE_URL


class EnrichmentObjects:
    @staticmethod
    def get_last_wh_uploads(workspace_id, destination_id, n=10, status=None, timeout=60):
        url = f"{RUDDER_CONFIG_BACKEND_SERVICE_BASE_URL}/admin/workspaces/{workspace_id}/uploads?destinationId={destination_id}&limit={n}&offset=0"
        if status:
            url = f"{url}&status={status}"
        try:
            response = ConfigBackendClient.get(url, timeout=timeout).json()
            if response.status_code != 200:
                raise Exception(response.text)
            if 'uploads' in response:
                return response['uploads']
            return []
        except Exception as e:
            logging.error(f"RudderEnrichment: Error fetching warehouse uploads {e}", exc_info=True)
            return {"wh_uploads_url": url}

    @staticmethod
    def __add_query_params_to_url(url, parameters):
        if not isinstance(parameters, dict):
            parameters = dict()
        implicit_params = {"utm_source": "notisvc", "utm_medium": "email"}
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update({**implicit_params, **parameters})
        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)

    @staticmethod
    def upload_aborted(destination_id, workspace_id, name, url, severity, workspace_metadata=None):
        incident_time = datetime.datetime.utcnow().strftime("%d-%b-%y %H:%M")
        wh_uploads = EnrichmentObjects.get_last_wh_uploads(workspace_id, destination_id, status='aborted')
        try:
            first_line = f'Hello {workspace_metadata.company_name or ""} Team'
        except Exception as e:
            first_line = 'Hello Team'
        email_title = f"Warehouse Upload Aborted | {name}"
        button_name = f'View {name} syncs'
        if severity != 'normal':
            email_body = f"""
            {first_line},<br/>
            We have been alerted that your {name} warehouse destination has failed syncing.<br/>
            This error occurred at {incident_time} utc.<br/>
            - RudderStack Team
            """
            email_body_heading = "Upload Aborted"
            button_name = f'View {name} syncs'
        else:
            email_body = f"""
            {first_line},<br/>
            The warehouse destination {name} sync is normal and operational.
            - RudderStack Team
            """
            email_body_heading = "Upload Sync Normal"
        _url = EnrichmentObjects.__add_query_params_to_url(url, {"tab": "Syncs"})
        return {"title": email_title, "body": email_body, "email_button_url": _url,
                "email_body_heading": email_body_heading, 'button_name': button_name,
                'metadata': {'wh_uploads': wh_uploads, 'destination_id': destination_id, 'workspace_id': workspace_id}}

    @staticmethod
    def proc_num_ut_output_failed_events(transformation_id, workspace_id, name, url, severity, destination_list, workspace_metadata=None):
        incident_time = datetime.datetime.utcnow().strftime("%d-%b-%y %H:%M")
        
        destination_line = ''
        if len(destination_list) > 0:
            destination_line = f"""<br/>This transformation is connected to the following destinations:<br/>{ ''.join([ f'- <b>{name}</b> <br/>' for name in destination_list ]) } <br/>"""
        
        email_title = f"Transformation Event Failures | {name}"
        button_name = f'View {name} transformation'
        if severity != 'normal':
            email_body = f"""
            Hi,<br/> 
            We have observed that the following transformation has caused some of your events to fail: <b>{name}</b> <br/> {destination_line} 
            This failure occurred on {incident_time} UTC.<br/>
            """
            email_body_heading = "User Transformation"
            button_name = f'View {name} Transformation'
        else:
            email_body = f"""
            Hi,<p/>
            The user transformation {name} sync is normal and operational.
            - RudderStack Team
            """
            email_body_heading = "Events flow is back to Normal"
        return {"title": email_title, "body": email_body, "email_button_url": url,
                "email_body_heading": email_body_heading, 'button_name': button_name,
                'metadata': {'workspace_id': workspace_id}}

    @staticmethod
    def warehouse_load_table_column_count(destination_id, workspace_id, name, url, severity, workspace_metadata=None):
        incident_time = datetime.datetime.utcnow().strftime("%d-%b-%y %H:%M")
        try:
            first_line = f'Hello {workspace_metadata.company_name or ""} Team'
        except Exception as e:
            first_line = 'Hello Team'
        email_title = f"Warehouse Column Count | {name}"
        button_name = f'View {name} destination'
        doc_url = 'https://www.rudderstack.com/docs/destinations/warehouse-destinations/json-column-support/'
        if severity != 'normal':
            email_body = f"""
            {first_line},<br/>
            We have been alerted that your {name} destination has reached the column count threshold.<br/>
            This occurred at {incident_time} utc.<br/><br/> 
            Please check if this is expected. If not, here are a few recommendations to avoid sync failures 
            in the future:<br/>
            1. Clean up columns that are not necessary - this will help us add new columns as necessary.<br/>
            2. If you have any JSON objects with dynamic properties in your event payload, flattening them could 
            effectively cause this situation to arise. You might want to instrument your events to avoid flattening 
            such JSON objects by following this doc <a href="{doc_url}" target="_blank">here</a>.
            <br/><br/> 
            - RudderStack Team
            """
            email_body_heading = "Warehouse Column Count"
            button_name = f'View {name} destination'
        else:
            email_body = f"""
            {first_line},<br/>
            The warehouse destination {name} column count threshold is normal.
            - RudderStack Team
            """
            email_body_heading = "Warehouse Column Count Normal"
        return {"title": email_title, "body": email_body, "email_button_url": url,
                "email_body_heading": email_body_heading, 'button_name': button_name,
                'metadata': {'destination_id': destination_id, 'workspace_id': workspace_id}}
