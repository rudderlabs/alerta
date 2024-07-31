from .BaseDittoEnrichment import BaseDittoEnrichment

class DestinationDittoEnrichment(BaseDittoEnrichment):
    def __init__(self, alert_type, ditto_variant_base_name, destination, destination_id, destination_deleted, workspace_id, url, severity,
                 workspace_metadata, raw_data, resource_info):
        self.destination = destination
        self.destination_id = destination_id
        self.destination_deleted = destination_deleted
        self.resource_info = resource_info
        super().__init__(alert_type, ditto_variant_base_name, workspace_id, url, severity, workspace_metadata, raw_data)

    def get_target_name(self):
        return self.destination

    def build_var_values_map(self, **kwargs):
        var_values_map = super(DestinationDittoEnrichment, self).build_var_values_map(**kwargs)
        var_values_map['destination'] = self.destination
        var_values_map['destination_id'] = self.destination_id

        return var_values_map

    def build_alert_metadata_map(self, **kwargs):
        alert_metadata_map = super(DestinationDittoEnrichment, self).build_alert_metadata_map(**kwargs)
        alert_metadata_map['resource_type'] = 'destination'
        alert_metadata_map['resource_id'] = self.destination_id
        alert_metadata_map['name'] = self.destination
        alert_metadata_map['resource_deleted'] = self.destination_deleted
        alert_metadata_map['resource_definition_id'] = self.resource_info.get('destinationDefinition', {}).get('id')
        alert_metadata_map['resource_definition_name'] = self.resource_info.get('destinationDefinition', {}).get('displayName')
        alert_metadata_map['category'] = self.resource_info.get('destinationDefinition', {}).get('category')
        return alert_metadata_map
