from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

from alerta.app import db

JSON = Dict[str, Any]


class AlertMetadata:

    def __init__(self, alert: str, resource_type: str, ditto_variant: str, **kwargs) -> None:

        self.alert = alert
        self.resource_type = resource_type
        self.ditto_variant = ditto_variant
        self.create_time = kwargs.get('create_time', None)
        self.update_time = kwargs.get('update_time', None)

    @classmethod
    def parse(cls, json: JSON) -> 'AlertMetadata':
        alert_metadata = AlertMetadata (
            alert = json.get('alert'),
            resource_type = json.get('resourceType'),
            ditto_variant = json.get('dittoVariant')
        )

        return alert_metadata

    @property
    def serialize(self) -> Dict[str, Any]:
        return {
            'alert': self.alert,
            'resourceType': self.resource_type,
            'dittoVariant': self.ditto_variant,
            'createTime': self.create_time,
            'updateTime': self.update_time
        }

    @classmethod
    def from_record(cls, rec) -> 'AlertMetadata':
        return AlertMetadata(
            alert=rec.alert,
            resource_type=rec.resource_type,
            ditto_variant=rec.ditto_variant,
            create_time=rec.create_time,
            update_time=rec.update_time
        )

    @classmethod
    def from_db(cls, r: Union[Dict, Tuple]) -> 'AlertMetadata':
        if isinstance(r, dict):
            return cls.from_document(r)
        elif isinstance(r, tuple):
            return cls.from_record(r)

    def create(self):
        return AlertMetadata.from_db(db.create_alert_metadata(self))
    
    def update(self, **kwargs) -> 'AlertMetadata':
        self.update_time = datetime.utcnow()
        return AlertMetadata.from_db(db.update_alert_metadata_by_alert(self.alert, self, **kwargs))
    
    @staticmethod
    def find_by_alert(alert: str) -> 'AlertMetadata':
        return AlertMetadata.from_db(db.get_alert_metada_by_alert(alert))

    @staticmethod
    def find_all() -> List['AlertMetadata']:
        return [AlertMetadata.from_db(channel) for channel in
                db.get_alert_metadata()]
