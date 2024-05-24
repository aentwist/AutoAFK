from textwrap import dedent
from typing import TypedDict

import requests
import settings


class Telegram(object):

    def __init__(self, chat_id: int, token: str, disable_notification: bool = False):
        self.chat_id = chat_id
        self.telegram_api = f"https://api.telegram.org/bot{token}/sendMessage"
        self.disable_notification = disable_notification

    def send(self, message: str) -> None:
        requests.post(
            url=self.telegram_api,
            data={
                "chat_id": self.chat_id,
                "text": dedent(message),
                "disable_web_page_preview": True,
                "disable_notification": self.disable_notification,
            },
        )


if settings.app_settings["enable_telegram"]:
    telegram = Telegram(
        settings.app_settings["chat_id"],
        settings.app_settings["token"],
    )
