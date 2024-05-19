import configparser
from textwrap import dedent
from typing import TypedDict

import requests

config = configparser.ConfigParser()
config.read("settings.ini")


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


class TelegramSettings(TypedDict):
    enable_telegram: bool
    token: str
    chat_id: int


telegram_settings: TelegramSettings = {
    "enable_telegram": config.getboolean("TELEGRAM", "enable"),
    "token": config.get("TELEGRAM", "token"),
    "chat_id": config.getint("TELEGRAM", "chat_id"),
}

if config.has_section("TELEGRAM") and telegram_settings["enable_telegram"]:
    telegram = Telegram(
        telegram_settings["chat_id"],
        telegram_settings["token"],
    )
