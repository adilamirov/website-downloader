from enum import Enum

import mongoengine as me
from flask_mongoengine import Document


class ScrapperTaskStatus(Enum):
    CREATED = 0
    IN_PROGRESS = 1
    FAILED = 2
    COMPLETE = 3


class ScrapperTaskDocument(Document):
    url = me.StringField(required=True)
    status = me.IntField(
        max_length=3,
        choices=[e.value for e in ScrapperTaskStatus],
        default=ScrapperTaskStatus.CREATED.value,
        required=True
    )
    download_link = me.StringField(
        default=None
    )

    meta = {'collection': 'tasks'}

    def to_json(self, *args, **kwargs):
        return {
            'id': str(self.id),
            'url': self.url,
            'status': ScrapperTaskStatus(self.status).name,
            'download_link': self.download_link,
        }
