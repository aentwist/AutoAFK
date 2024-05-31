import enum
import json
import sys
import threading
from typing import TypedDict

from autoafk import activities, settings, thread_state
from autoafk.logger import logger, setup_logging
from autoafk.thread_state import handle_pause_and_stop_events, pause_event, stop_event
from autoafk.tools import connect as tools_connect


class MessageType(enum.Enum):
    CONNECT = "CONNECT"
    RUN = "RUN"
    PAUSE = "PAUSE"
    STOP = "STOP"


class Message(TypedDict):
    type: MessageType


class SettingsMessage(Message):
    app_settings: settings.AppSettings


class Task:
    fn: str
    name: str
    # TODO: NotRequired
    settings: dict[str, bool | int | str]


class RunMessage(SettingsMessage):
    tasks: list[Task]


def connect(message: SettingsMessage) -> None:
    settings.app_settings = message["app_settings"]
    tools_connect()


def run_tasks(tasks: list[Task]) -> None:
    for task in tasks:
        handle_pause_and_stop_events()

        # Call the task fn with the task settings, if any
        # Separate dict index from f-string so black still loves us
        # See https://github.com/psf/black/issues/3747
        task_name = task["name"]
        logger.info(f"Running task {task_name}...")
        fn = getattr(activities, task["fn"])
        fn(task["settings"]) if "settings" in task else fn()

    # Made it through without stopping
    logger.info("Done")


def run(message: RunMessage) -> None:
    # TODO: Use a queue to allow queuing more tasks while tasks are running
    if not thread_state.thread or not thread_state.thread.is_alive():

        def fn() -> None:
            run_tasks(message["tasks"])

        settings.app_settings = message["app_settings"]
        thread_state.thread = threading.Thread(target=fn)
        thread_state.thread.start()


def pause(message: SettingsMessage) -> None:
    if not pause_event.is_set():
        logger.info("Pausing...")
        pause_event.set()
    else:
        logger.info("Continuing...")
        settings.app_settings = message["app_settings"]
        pause_event.clear()


def stop() -> None:
    logger.info("Stopping...")
    stop_event.set()


def main() -> None:
    setup_logging()

    while True:
        data = sys.stdin.readline()
        # Python chokes on escaped characters in f-strings...
        t = data.replace("\n", "")
        logger.debug(f"Received: {t}")
        message: Message = json.loads(data)

        if MessageType[message["type"]] is MessageType.CONNECT:
            connect(message)
        elif MessageType[message["type"]] is MessageType.RUN:
            run(message)
        elif MessageType[message["type"]] is MessageType.PAUSE:
            pause(message)
        elif MessageType[message["type"]] is MessageType.STOP:
            stop()
        else:
            message_type = message["type"]  # for black
            logger.error(f"Unrecognized message type {message_type}")
