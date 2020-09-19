from urllib.parse import urlparse

from broadcaster import Broadcast
from broadcaster._backends.base import BroadcastBackend


class EventsHandler(Broadcast):
    _backend: BroadcastBackend

    def __init__(self, url: str):
        super().__init__(url)

        parsed_url = urlparse(url)

        if parsed_url.scheme == 'kafka':
            from .backends.kafka import KafkaBackend

            self._backend = KafkaBackend(url)

        elif parsed_url.scheme == 'gcloud-pubsub':
            from .backends.gcloud_pubsub import GCloudPubSubBackend

            self._backend = GCloudPubSubBackend(url)
