import enum
import logging

from alerta.plugins import PluginBase
from alerta.stats import StatsD
from expiringdict import ExpiringDict

from rudder_enrichment.config_backend_client import ConfigBackendClient
from rudder_enrichment.environment import RUDDER_CONFIG_BACKEND_CACHE_STORE_MAX_SIZE, \
    RUDDER_CONFIG_BACKEND_DATA_CACHE_TTL, \
    RUDDER_CONFIG_BACKEND_SERVICE_BASE_URL
from rudder_enrichment.rudder_enrichment_models import Source, Destination, Workspace, Transformation
from rudder_enrichment.rudder_enrichment_models.Connection import Connection

log_object = logging.getLogger('alerta.plugins.rudder_enrichment')

sources_search_words = ['sourceID=', 'sourceId=', 'source-id=', 'source=', 'source_id=']
destinations_search_words = ['destID=', 'destinationId=', 'destinationID=', 'destination-id=', 'destId=', 'destination_id=']
transformation_search_words = ['transformationId=', 'transformation_id=']


class CacheStoreKeys(enum.Enum):
    SOURCES = "sources"
    DESTINATIONS = "destinations"
    WORKSPACE = "workspaces"
    TRANSFORMATIONS = "transformations"


class CacheStore:
    def __init__(self, storage_object_type):
        self.storage_object_type: CacheStoreKeys = storage_object_type
        self.cache_store = ExpiringDict(max_len=RUDDER_CONFIG_BACKEND_CACHE_STORE_MAX_SIZE,
                                        max_age_seconds=RUDDER_CONFIG_BACKEND_DATA_CACHE_TTL)

    def set_cache_store(self, key):
        try:
            url = f'{RUDDER_CONFIG_BACKEND_SERVICE_BASE_URL}/admin/{self.storage_object_type.value}/{key}'
            with StatsD.stats_client.timer("enrichment_cb_lookup_time"):
                r = ConfigBackendClient.get(url)
            if r.status_code != 200:
                raise Exception(r.text)
            if self.storage_object_type == CacheStoreKeys.SOURCES:
                dao_object = Source.from_json(r.json())
            elif self.storage_object_type == CacheStoreKeys.DESTINATIONS:
                dao_object = Destination.from_json(r.json())
            elif self.storage_object_type == CacheStoreKeys.TRANSFORMATIONS:
                dao_object = Transformation.from_json(r.json())
            else:
                dao_object = Workspace.from_json(r.json())
            self.cache_store[key] = dao_object
            return self.cache_store[key]
        except Exception as e:
            StatsD.increment("enrichment_cb_lookup_error", 1,
                             tags={"object_type": self.storage_object_type.value, "object_id": key,
                                   "type": self.storage_object_type.value})
            log_object.error(f"RudderEnrichment: Error setting cache store {e}", exc_info=True)
            return None

    def get_or_set(self, key):
        try:
            return self.cache_store[key]
        except KeyError as e:
            StatsD.increment("enrichment_cache_miss", 1, tags={"id": key, "type": self.storage_object_type.value})
            return self.set_cache_store(key)


class RudderEnrichment(PluginBase):
    def __init__(self, name=None):
        log_object.info("RudderEnrichment: Initialized")
        self.sources_cache = CacheStore(CacheStoreKeys.SOURCES)
        self.destinations_cache = CacheStore(CacheStoreKeys.DESTINATIONS)
        self.workspaces_cache = CacheStore(CacheStoreKeys.WORKSPACE)
        self.transformations_cache = CacheStore(CacheStoreKeys.TRANSFORMATIONS)
        super(RudderEnrichment, self).__init__(name)

    @staticmethod
    def get_matched_tag_value(tags: list, search_words: list):
        for tag in tags:
            for search_word in search_words:
                if tag.startswith(search_word):
                    return tag.replace(search_word, '')

    def get_metadata(self, store, key):
        if store == CacheStoreKeys.SOURCES:
            return self.sources_cache.get_or_set(key)
        elif store == CacheStoreKeys.DESTINATIONS:
            return self.destinations_cache.get_or_set(key)
        elif store == CacheStoreKeys.WORKSPACE:
            return self.workspaces_cache.get_or_set(key)
        elif store == CacheStoreKeys.TRANSFORMATIONS:
            return self.transformations_cache.get_or_set(key)

    def search_connections(self, alert):
        enriched = False
        source_id = self.get_matched_tag_value(alert.tags, sources_search_words)
        destination_id = self.get_matched_tag_value(alert.tags, destinations_search_words)
        if source_id and destination_id:
            source_metadata: Source = self.get_metadata(CacheStoreKeys.SOURCES, source_id)
            destination_metadata: Destination = self.get_metadata(CacheStoreKeys.DESTINATIONS, destination_id)
            if source_metadata and destination_metadata:
                workspace_metadata: Workspace = self.get_metadata(CacheStoreKeys.WORKSPACE,
                                                                  source_metadata.workspaceId)
                source_metadata.workspace_metadata = workspace_metadata
                destination_metadata.workspace_metadata = workspace_metadata
                connection_metadata = Connection(source_metadata, destination_metadata)
                alert = connection_metadata.enrich_alert(alert)
                if workspace_metadata:
                    alert = workspace_metadata.enrich_alert(alert)
                enriched = True
            else:
                StatsD.stats_client.incr("enrichment_source_cb_lookup_err", 1,
                                         tags={"source_id": source_id, "alert_id": alert.id})
        return alert, enriched

    def search_sources(self, alert):
        enriched = False
        source_id = self.get_matched_tag_value(alert.tags, sources_search_words)
        if source_id:
            source_metadata: Source = self.get_metadata(CacheStoreKeys.SOURCES, source_id)
            if source_metadata:
                workspace_metadata: Workspace = self.get_metadata(CacheStoreKeys.WORKSPACE,
                                                                  source_metadata.workspaceId)
                source_metadata.workspace_metadata = workspace_metadata
                alert = source_metadata.enrich_alert(alert)
                if workspace_metadata:
                    alert = workspace_metadata.enrich_alert(alert)
                enriched = True
            else:
                StatsD.stats_client.incr("enrichment_source_cb_lookup_err", 1,
                                         tags={"source_id": source_id, "alert_id": alert.id})
        return alert, enriched

    def search_destinations(self, alert):
        enriched = False
        destination_id = self.get_matched_tag_value(alert.tags, destinations_search_words)
        if destination_id:
            destination_metadata: Destination = self.get_metadata(CacheStoreKeys.DESTINATIONS, destination_id)
            if destination_metadata:
                workspace_metadata: Workspace = self.get_metadata(CacheStoreKeys.WORKSPACE,
                                                                  destination_metadata.workspaceId)
                destination_metadata.workspace_metadata = workspace_metadata
                alert = destination_metadata.enrich_alert(alert)
                if workspace_metadata:
                    alert = workspace_metadata.enrich_alert(alert)
                enriched = True
            else:
                StatsD.stats_client.incr("enrichment_destination_cb_lookup_err", 1,
                                         tags={"destination_id": destination_id, "alert_id": alert.id})
        return alert, enriched
    
    def search_transformations(self, alert):
        enriched = False
        transformation_id = self.get_matched_tag_value(alert.tags, transformation_search_words)
        if transformation_id:
            transformation_metadata: Transformation = self.get_metadata(CacheStoreKeys.TRANSFORMATIONS, transformation_id)
            if transformation_metadata:
                workspace_metadata: Workspace = self.get_metadata(CacheStoreKeys.WORKSPACE,
                                                                  transformation_metadata.workspaceId)
                transformation_metadata.workspace_metadata = workspace_metadata
                alert = transformation_metadata.enrich_alert(alert)
                if workspace_metadata:
                    alert = workspace_metadata.enrich_alert(alert)
                enriched = True
            else:
                StatsD.stats_client.incr("enrichment_destination_cb_lookup_err", 1,
                                         tags={"transformation_id": transformation_id, "alert_id": alert.id})
        return alert, enriched

    def enrich_alert(self, alert):
        methods = [self.search_connections, self.search_sources, self.search_destinations, self.search_transformations]

        for method in methods:
            alert, enriched = method(alert)
            if enriched and alert.enriched_data:
                return alert

        logging.error(f"RudderEnrichment: failed to enrich alert {alert}")
        StatsD.stats_client.incr("enrichment_error", 1, tags={"alert_resource": alert.resource})
        raise RuntimeError(f"RudderEnrichment: Workspace id could not be extracted from sources,destinations,workspace for alert {alert.id}")

    def pre_receive(self, alert, *args, **kwargs):
        if alert.repeat:
            log_object.debug('RudderEnrichment: skipping enrichment for repeated alert')
            return alert
        log_object.debug('RudderEnrichment: pre_receive %s', alert)
        return self.enrich_alert(alert)

    def post_receive(self, alert, *args, **kwargs):
        return alert

    def status_change(self, alert, status, text, *args, **kwargs):
        if alert.repeat:
            log_object.debug('RudderEnrichment: skipping enrichment for repeated alert')
            return alert

        log_object.info("RudderEnrichment: status_change %s %s %s", alert, status, text)
        alert.status = status
        alert.text = text
        
        if status == 'expired':
            log_object.debug('RudderEnrichment: skipping enrichment for expired alert')
            return alert
        
        return self.enrich_alert(alert)
