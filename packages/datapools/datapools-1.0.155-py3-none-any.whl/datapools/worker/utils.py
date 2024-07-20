from urllib.parse import urlunparse, urlparse

from ..common.queues import QueueMessageType


def get_storage_invalidation_topic(worker_id):
    return f"worker.id_{worker_id}.type_{QueueMessageType.StorageInvalidation.value}"


def get_url_study_response_topic(receiver_id):
    return f"url_study_response.id_{receiver_id}"


def canonicalize_url(url):
    # Normalize the URL to a standard form
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path if p.path != "/" else "", p.params, p.query, ""))
