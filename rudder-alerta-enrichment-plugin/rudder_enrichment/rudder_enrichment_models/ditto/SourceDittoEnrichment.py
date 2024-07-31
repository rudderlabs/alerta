from .BaseDittoEnrichment import BaseDittoEnrichment

class SourceDittoEnrichment(BaseDittoEnrichment):
    def __init__(self, alert_type, ditto_variant_base_name, source, source_id, source_deleted, workspace_id, url, severity,
                 workspace_metadata, raw_data, resource_info):
        self.source = source
        self.source_id = source_id
        self.source_deleted = source_deleted
        self.resource_info = resource_info
        super().__init__(alert_type, ditto_variant_base_name, workspace_id, url, severity, workspace_metadata, raw_data)

    def get_target_name(self):
        return self.source

    def build_var_values_map(self, **kwargs):
        var_values_map = super(SourceDittoEnrichment, self).build_var_values_map(**kwargs)
        var_values_map['source'] = self.source
        var_values_map['source_id'] = self.source_id

        return var_values_map

    def build_alert_metadata_map(self, **kwargs):
        alert_metadata_map = super(SourceDittoEnrichment, self).build_alert_metadata_map(**kwargs)
        alert_metadata_map['resource_type'] = 'source'
        alert_metadata_map['resource_id'] = self.source_id
        alert_metadata_map['name'] = self.source
        alert_metadata_map['resource_deleted'] = self.source_deleted
        alert_metadata_map['resource_definition_id'] = self.resource_info.get('sourceDefinition', {}).get('id')
        alert_metadata_map['resource_definition_name'] = self.resource_info.get('sourceDefinition', {}).get('displayName')
        alert_metadata_map['category'] = self.resource_info.get('sourceDefinition', {}).get('category')

        return alert_metadata_map


