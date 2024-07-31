from .BaseDittoEnrichment import BaseDittoEnrichment


class TransformationDittoEnrichment(BaseDittoEnrichment):
    def __init__(self, alert_type, ditto_variant_base_name, transformation, transformation_id, workspace_id, url,
                 severity,
                 workspace_metadata,
                 raw_data,
                 resource_info):
        self.transformation = transformation
        self.transformation_id = transformation_id
        self.resource_info = resource_info
        super().__init__(alert_type, ditto_variant_base_name, workspace_id, url, severity, workspace_metadata, raw_data)

    def get_target_name(self):
        return self.transformation

    def build_var_values_map(self, **kwargs):
        var_values_map = super(TransformationDittoEnrichment, self).build_var_values_map(**kwargs)
        var_values_map['transformation'] = self.transformation
        var_values_map['transformation_id'] = self.transformation_id

        return var_values_map

    def build_alert_metadata_map(self, **kwargs):
        alert_metadata_map = super(TransformationDittoEnrichment, self).build_alert_metadata_map(**kwargs)
        alert_metadata_map['transformation_id'] = self.transformation_id

        alert_metadata_map['resource_type'] = 'transformation'
        alert_metadata_map['resource_id'] = self.transformation_id
        alert_metadata_map['name'] = self.transformation

        return alert_metadata_map
