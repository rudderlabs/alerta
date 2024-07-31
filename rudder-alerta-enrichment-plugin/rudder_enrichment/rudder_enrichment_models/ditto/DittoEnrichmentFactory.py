from rudder_enrichment.rudder_enrichment_models.constants import AlertTargetType
from .SourceDittoEnrichment import SourceDittoEnrichment
from .TransformationDittoEnrichment import TransformationDittoEnrichment
from .DestinationDittoEnrichment import DestinationDittoEnrichment
from .ConnectionDittoEnrichment import ConnectionDittoEnrichment
from rudder_enrichment.environment import ALERT_METADATA_CONFIG_FILE
import json
import logging

class DittoEnrichmentFactory:

    @staticmethod
    def get_instance(alert_type, processed_target_type, severity, raw_data, source=None, destination=None, transformation=None):
        alert_metadata = DittoEnrichmentFactory.get_alert_metadata(alert_name=alert_type)
        dittoVariant = alert_metadata.get('dittoVariant')
        identified_target_type = alert_metadata.get('resourceType')

        if identified_target_type is None or identified_target_type != processed_target_type.value:
            return None
        
        if identified_target_type == AlertTargetType.CONNECTION.value:
            return ConnectionDittoEnrichment(
                alert_type=alert_type,
                ditto_variant_base_name=dittoVariant,
                source=source.name,
                source_id=source.id,
                source_deleted=source.deleted,
                source_info=source.resource_info,
                url=source.url,
                destination=destination.name,
                destination_id=destination.id,
                destination_deleted=destination.deleted,
                destination_info=destination.resource_info,
                workspace_id=source.workspaceId,
                workspace_metadata=source.workspace_metadata,
                severity=severity,
                raw_data=raw_data
            )
        elif identified_target_type == AlertTargetType.SOURCE.value:
            return SourceDittoEnrichment(
                alert_type=alert_type,
                ditto_variant_base_name=dittoVariant,
                source=source.name,
                source_id=source.id,
                source_deleted=source.deleted,
                workspace_id=source.workspaceId,
                url=source.url,
                severity=severity,
                workspace_metadata=source.workspace_metadata,
                raw_data=raw_data,
                resource_info=source.resource_info
            )
        elif identified_target_type == AlertTargetType.TRANSFORMATION.value:
            return TransformationDittoEnrichment(
                alert_type=alert_type,
                ditto_variant_base_name=dittoVariant,
                transformation=transformation.name,
                transformation_id=transformation.id,
                workspace_id=transformation.workspaceId,
                url=transformation.url,
                severity=severity,
                workspace_metadata=transformation.workspace_metadata,
                raw_data=raw_data,
                resource_info=transformation.resource_info
            )
        elif identified_target_type == AlertTargetType.DESTINATION.value:
            return DestinationDittoEnrichment(
                alert_type=alert_type,
                ditto_variant_base_name=dittoVariant,
                destination=destination.name,
                destination_id=destination.id,
                destination_deleted=destination.deleted,
                workspace_id=destination.workspaceId,
                url=destination.url,
                severity=severity,
                workspace_metadata=destination.workspace_metadata,
                raw_data=raw_data,
                resource_info=destination.resource_info
            )

        return None


    @staticmethod
    def get_alert_metadata(alert_name):
        try:
            with open(ALERT_METADATA_CONFIG_FILE, 'r') as f:
                alert_metadata = json.load(f)['alertMetadata']
            return alert_metadata[alert_name]
        except Exception as e:
            logging.error(f"Error loading alert metadata; {e}", exc_info=True)
