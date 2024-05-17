import configparser
from textwrap import dedent

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


if config.has_section("TELEGRAM") and config.getboolean("TELEGRAM", "enable"):

    # Initialize the Telegram object
    telegram = Telegram(
        chat_id=config.getint("TELEGRAM", "chat_id"),
        token=config.get("TELEGRAM", "token"),
    )

    # Custom print function that duplicates output to console and Telegram
    def print_and_send_to_telegram(*args, **kwargs):
        # Convert all arguments to strings and join them
        message = " ".join(map(str, args))

        # Print to console
        built_in_print(*args, **kwargs)

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
