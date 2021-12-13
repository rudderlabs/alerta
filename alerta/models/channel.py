from typing import Any, Dict, List, Optional, Tuple, Union

import validators

from alerta.app import db

JSON = Dict[str, Any]


class CustomerChannel:
    SUPPORTED_CHANNEL_TYPES = ["webhook", "email"]

    def __init__(self, name, channel_type, properties, customer_id, id=None):
        self.id = id
        self.name = name
        self.channel_type = channel_type
        self.properties = properties
        self.customer_id = customer_id

    def create(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise Exception("Channel name must be a valid text value")
        if self.channel_type not in CustomerChannel.SUPPORTED_CHANNEL_TYPES:
            raise Exception(f"Support channel types are {CustomerChannel.SUPPORTED_CHANNEL_TYPES}")
        if not isinstance(self.properties, dict):
            raise Exception("Channel properties are required to create channel")
        if self.channel_type == "email":
            emails = self.properties.get("emails", [])
            if not isinstance(emails, list) or len(emails) == 0:
                raise Exception("Emails list cannot be empty")
            for index, email in enumerate(emails):
                if not validators.email(email):
                    raise Exception(f"Email value at position {index + 1} is not valid")
        elif self.channel_type == "webhook":
            url = self.properties.get('url')
            if not validators.url(url):
                raise Exception("Webhook property 'url' is required and cannot be empty")
        return CustomerChannel.from_db(db.create_channel(self))

    @classmethod
    def from_record(cls, rec) -> 'CustomerChannel':
        return CustomerChannel(rec.name, rec.channel_type, rec.properties, rec.customer_id, rec.id)

    @classmethod
    def from_db(cls, r: Union[Dict, Tuple]) -> 'CustomerChannel':
        if isinstance(r, dict):
            return cls.from_document(r)
        elif isinstance(r, tuple):
            return cls.from_record(r)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "channel_type": self.channel_type,
            "properties": self.properties,
            "customer_id": self.customer_id
        }

    @staticmethod
    def find_all(customer_id, sort_by, ascending, limit, offset):
        return [CustomerChannel.from_db(channel) for channel in
                db.get_channels(customer_id, sort_by, ascending, limit, offset)]

    @staticmethod
    def find_by_id(channel_id):
        return CustomerChannel.from_db(db.find_channel_by_id(channel_id))

    @staticmethod
    def update_by_id(channel_id, name=None, properties=None, **kwargs):
        return CustomerChannel.from_db(db.update_channel_by_id(channel_id, name, properties))

    @staticmethod
    def delete_by_id(channel_id):
        return CustomerChannel.from_db(db.delete_channel_by_id(channel_id))

    @classmethod
    def parse(cls, json: JSON) -> 'Rule':
        if not isinstance(json.get('name'), str) or json.get('name').strip() == "":
            raise Exception("Channel name is required, it must be a string")
        if json.get('channel_type') not in CustomerChannel.SUPPORTED_CHANNEL_TYPES:
            raise Exception(f"Channel type must be one of {CustomerChannel.SUPPORTED_CHANNEL_TYPES}")
        if not isinstance(json.get('properties'), dict):
            raise Exception("Channel properties are required")
        if not isinstance(json.get('customer_id'), str) or json.get('customer_id').strip() == "":
            raise Exception("customer_id is required, it must be a string")
        return CustomerChannel(**json)
