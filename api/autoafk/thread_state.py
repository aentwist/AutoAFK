import threading
from time import sleep

from autoafk.logger import logger


# Offload tasks onto a separate thread so we can continue to receive commands
# while it runs. Note that games must be played synchronously so just 1 thread
# per game is fine.
thread: threading.Thread = None
pause_event = threading.Event()
stop_event = threading.Event()


# This needs to be its own function so we can call it from very long looping
# tasks to maintain responsiveness (such as pushing and lab in AFK Arena)
def handle_pause_and_stop_events() -> None:
    # Memorize state to give better feedback on state changes
    paused_state = False

    # Handle pause events before stop events because we could stop out of a
    # paused state. Parameter sleep time determines the load vs.
    # responsiveness trade-off.
    while pause_event.is_set() and not stop_event.is_set():
        if not paused_state:
            paused_state = True
            logger.info("Paused")
        sleep(1)

    # Handle stop events
    if stop_event.is_set():
        stop_event.clear()
        # Also clear the pause event here in case we stop out of a paused state
        pause_event.clear()
        logger.info("Stopped")
        # Exit so this will get us out even from deep in the call stack
        exit(0)

    # Send unpauses after stop event handling to not send if stopped
    if paused_state:
        paused_state = False
        logger.info("Unpaused")
