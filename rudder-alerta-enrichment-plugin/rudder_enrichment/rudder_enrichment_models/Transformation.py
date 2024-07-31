import logging

from rudder_enrichment.environment import RUDDER_WEB_APP_URL_PREFIX
from rudder_enrichment.rudder_enrichment_models.constants import AlertTargetType
from rudder_enrichment.rudder_enrichment_models.Enrichment import EnrichmentObjects
from rudder_enrichment.rudder_enrichment_models.ditto import DittoEnrichmentFactory


class Transformation:
    workspace_metadata = None

    def __init__(self, id, name, description, workspaceId, createdAt, updatedAt, codeVersion, destinations=[], *args, **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.workspaceId = workspaceId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.codeVersion = codeVersion
        self.destinations = destinations
        self.resource_info = kwargs
        self.url = f"{RUDDER_WEB_APP_URL_PREFIX}/transformations/{self.id}"


    def enrich_alert(self, alert):
        alert.customer = self.workspaceId

        try:
            ditto_enricher = DittoEnrichmentFactory.get_instance(
                processed_target_type=AlertTargetType.TRANSFORMATION,
                transformation=self,
                alert_type=alert.resource,
                severity=alert.severity,
                raw_data=alert.raw_data
            )
            if ditto_enricher is not None:
                alert.enriched_data = ditto_enricher.enrich()
            else:

                enrichment_function = getattr(EnrichmentObjects, alert.resource)
                alert.enriched_data = enrichment_function(transformation_id=self.id, workspace_id=self.workspaceId,
                                                          url=self.url,
                                                          name=self.name,
                                                          severity=alert.severity,
                                                          destination_list=self.get_destination_list(self.destinations),
                                                          workspace_metadata=self.workspace_metadata)
        except Exception as e:
            logging.error(f"RudderEnrichment: Error enriching transformation {e}", exc_info=True)
            raise RuntimeError(f"RudderEnrichment: Error enriching transformation {e}")
        return alert

    def get_destination_list(self, destinations):
        return [ dest["name"] for dest in destinations ]

    @staticmethod
    def from_json(json_dict: dict):
        return Transformation(**json_dict)
