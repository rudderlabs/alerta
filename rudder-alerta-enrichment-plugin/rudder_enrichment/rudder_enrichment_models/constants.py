from enum import Enum


class AlertTargetType(Enum):
    SOURCE = 'source'
    TRANSFORMATION = 'transformation'
    DESTINATION = 'destination'
    CONNECTION = 'connection'
