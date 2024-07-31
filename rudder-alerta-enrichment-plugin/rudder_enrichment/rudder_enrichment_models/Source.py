import logging

from rudder_enrichment.environment import RUDDER_WEB_APP_URL_PREFIX
from rudder_enrichment.rudder_enrichment_models.constants import AlertTargetType
from rudder_enrichment.rudder_enrichment_models.Enrichment import EnrichmentObjects
from rudder_enrichment.rudder_enrichment_models.ditto import DittoEnrichmentFactory

class Source:
    def __init__(self, id, name, writeKey, enabled, config, workspaceId, createdAt, deleted, *args, **kwargs):
        self.id = id
        self.name = name
        self.writeKey = writeKey
        self.enabled = enabled
        self.config = config
        self.workspaceId = workspaceId
        self.createdAt = createdAt
        self.deleted = deleted
        self.resource_info = kwargs
        self.url = f"{RUDDER_WEB_APP_URL_PREFIX}/sources/{self.id}"

    def enrich_alert(self, alert):
        alert.customer = self.workspaceId
        try:
            ditto_enricher = DittoEnrichmentFactory.get_instance(
                processed_target_type=AlertTargetType.SOURCE,
                source=self,
                alert_type=alert.resource,
                severity=alert.severity,
                raw_data=alert.raw_data
            )
            if ditto_enricher is not None:
                alert.enriched_data = ditto_enricher.enrich()
            else:
                enrichment_function = getattr(EnrichmentObjects, alert.resource)
                alert.enriched_data = enrichment_function(source_id=self.id, workspace_id=self.workspaceId,
                                                          url=self.url,
                                                          name=self.name,
                                                          severity=alert.severity,
                                                          workspace_metadata=self.workspace_metadata)
        except Exception as e:
            logging.error(f"RudderEnrichment: Error enriching source {e}", exc_info=True)
            raise RuntimeError(f"RudderEnrichment: Error enriching source {e}")
        return alert

    @staticmethod
    def from_json(json_dict: dict):
        return Source(**json_dict)
