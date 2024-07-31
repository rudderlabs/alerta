from .BaseDittoEnrichment import BaseDittoEnrichment

class ConnectionDittoEnrichment(BaseDittoEnrichment):
    def __init__(self, alert_type, ditto_variant_base_name, source, source_id, source_deleted, source_info, 
                 destination, destination_id, destination_deleted, destination_info, 
                 workspace_id, url, severity, workspace_metadata, raw_data):
        self.source = source
        self.source_id = source_id
        self.source_deleted = source_deleted
        self.destination = destination
        self.destination_id = destination_id
        self.destination_deleted = destination_deleted
        self.source_info = source_info
        self.destination_info = destination_info
        super().__init__(alert_type, ditto_variant_base_name, workspace_id, url, severity, workspace_metadata, raw_data)

    def get_target_name(self):
        return self.destination

    def build_var_values_map(self, **kwargs):
        var_values_map = super(ConnectionDittoEnrichment, self).build_var_values_map(**kwargs)
        var_values_map['source'] = self.source
        var_values_map['source_id'] = self.source_id
        var_values_map['destination'] = self.destination
        var_values_map['destination_id'] = self.destination_id

        return var_values_map

    def build_alert_metadata_map(self, **kwargs):
        alert_metadata_map = super(ConnectionDittoEnrichment, self).build_alert_metadata_map(**kwargs)
        alert_metadata_map['source_name'] = self.source
        alert_metadata_map['source_id'] = self.source_id
        alert_metadata_map['source_definition_id'] = self.source_info.get('sourceDefinition', {}).get('id')
        alert_metadata_map['source_definition_name'] = self.source_info.get('sourceDefinition', {}).get('displayName')
        
        alert_metadata_map['destination_name'] = self.destination
        alert_metadata_map['destination_id'] = self.destination_id
        alert_metadata_map['destination_definition_id'] = self.destination_info.get('destinationDefinition', {}).get('id')
        alert_metadata_map['destination_definition_name'] = self.destination_info.get('destinationDefinition', {}).get('displayName')
        alert_metadata_map['category'] = self.destination_info.get('destinationDefinition', {}).get('category')
        
        alert_metadata_map['resource_type'] = 'connection'
        alert_metadata_map['resource_deleted'] = self.source_deleted or self.destination_deleted
        
        return alert_metadata_map
