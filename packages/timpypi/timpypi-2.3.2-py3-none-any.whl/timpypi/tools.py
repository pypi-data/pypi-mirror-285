import json
import logging
from typing import Any
from requests import Request
from timpypi.common import exception
from timpypi.tiktok import effectRainbow, requestGeneral

_logger = logging.getLogger(__name__)


@exception
def __general__(callback: Any, callback_log: Any, other: Any | None,
                domain: str, api: str, method: Request,
                body: dict, params: dict, secret: str,
                keyword: str, key: str, notification: dict) -> Any:
    """
    @Description: General action step
    @Params: 
        callback: Function (Required)
        api: str (Required)
        method: Request (Required)
        body: dict() (Optional)
        keyword: access data (Required)
        notification: dict() (Required)
            title: str
            message: str
    @Return: Any or (...) -> Any
    """
    response = requestGeneral(method=method, domain=domain, api=api,
                              params=params, body=body, secret=secret, key=key)
    response = json.loads(response.text)
    callback_log(response)
    if response.get("code") == 0:
        data_list = response.get("data", {}).get(keyword, [])
        for data in data_list:
            try:
                callback(other, data)
            except Exception as e:
                _logger.error(e)
                continue
        return effectRainbow(message="Successfully")
    else:
        message = notification.get(
            "message") or "An error occurred during handle process"
        title = notification.get("title") or "Itegration Process"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                    "type": "danger",
                    "message": message,
                    "title": title,
                    "sticky": False,
                    'next': {'type': 'ir.actions.act_window_close'},
            }
        }
