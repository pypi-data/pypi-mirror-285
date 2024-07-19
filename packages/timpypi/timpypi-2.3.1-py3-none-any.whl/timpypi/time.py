from datetime import datetime
import logging
from timpypi.common import exception

_logger = logging.getLogger(__name__)


@exception
def timestampToDatetime(timestamp) -> datetime:
    if not (isinstance(timestamp, float) or isinstance(timestamp, int)):
        raise ValueError("Timestamp must be an integer or float")
    timestamp = float(timestamp)
    try:
        return datetime.fromtimestamp(timestamp)
    except ValueError as e:
        return datetime.fromtimestamp(timestamp / 1000)
