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

    # Initialize the Telegram object
    telegram = Telegram(
        telegram_settings["chat_id"],
        telegram_settings["token"],
    )

    # TODO: Remove
    # Custom print function that duplicates output to console and Telegram
    def log(*args, **kwargs):
        # Convert all arguments to strings and join them
        message = " ".join(map(str, args))

        # Print to console
        log(*args, **kwargs)

        # Check if message is empty
        if message.strip():
            # List of prefixes to check
            prefixes = ["ERR", "WAR", "GRE", "BLU", "PUR"]

            # Check if the message starts with any of the prefixes
            if any(message.startswith(prefix) for prefix in prefixes):
                # Start from the fourth character
                processed_message = message[3:]
                # Send processed message to Telegram
                telegram.send(processed_message)
            else:
                # Send the original message to Telegram
                telegram.send(message)

    # Save the built-in print function to avoid infinite recursion
    built_in_print = print

    # Replace the built-in print function with our custom function
    print = print_and_send_to_telegram
