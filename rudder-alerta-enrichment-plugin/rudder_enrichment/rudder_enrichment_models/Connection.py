import logging

from rudder_enrichment.rudder_enrichment_models import Source, Destination
from rudder_enrichment.rudder_enrichment_models.constants import AlertTargetType
from rudder_enrichment.rudder_enrichment_models.ditto import DittoEnrichmentFactory


class Connection:
    source_metadata: Source = None
    destination_metadata: Destination = None

    def __init__(self, source_metadata, destination_metadata, *args, **kwargs):
        self.source_metadata = source_metadata
        self.destination_metadata = destination_metadata

    def enrich_alert(self, alert):
        alert.customer = self.source_metadata.workspaceId
        try:
            ditto_enricher = DittoEnrichmentFactory.get_instance(
                processed_target_type=AlertTargetType.CONNECTION,
                source=self.source_metadata,
                destination=self.destination_metadata,
                alert_type=alert.resource,
                severity=alert.severity,
                raw_data=alert.raw_data,
            )

            alert.enriched_data = ditto_enricher.enrich()
        except Exception as e:
            logging.error(f"RudderEnrichment: Error enriching connection {e}", exc_info=True)
            raise RuntimeError(f"RudderEnrichment: Error enriching connection {e}")
        return alert
