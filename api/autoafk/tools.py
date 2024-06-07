import atexit
import enum
import io
import math
import os
import subprocess
import time

import numpy
import psutil
import pyscreeze
import scrcpy
from com.dtmilano.android.adb.adbclient import AdbClient
from com.dtmilano.android.viewclient import ViewClient
from PIL import Image

from autoafk import project_dir, settings, SRC_DIR
from autoafk.logger import logger


RESOLUTION = (1080, 1920)
DPI = 240


adb_client: AdbClient
scrcpy_client: scrcpy.Client


## Connect


def connect() -> None:
    global adb_client
    global scrcpy_client

    logger.info("Connecting...")

    _start_emulator()
    _start_adb_server()

    # Connect to device
    # TODO: Allow specifying serial number, e.g. emulator-5554
    # port = settings.app_settings["port"]
    # serial = f"127.0.0.1:{port}"
    # logger.debug(f"Connecting to device with serial {serial}...")
    logger.debug(f"Connecting to device...")
    adb_client, _ = ViewClient.connectToDeviceOrExit()  # serialno=serial

    # Start and connect to scrcpy
    logger.debug("Connecting to scrcpy...")
    scrcpy_client = scrcpy.Client(adb_client.serialno)
    scrcpy_client.start(daemon_threaded=True)
    # We need to wait for the scrcpy server to spin up...
    while True:
        try:
            get_frame()
            break
        except:
            wait()

    # Run checks and navigate to the starting position
    _check_device_resolution()
    _run_game()
    _wait_until_game_active()
    expand_menus()


def _is_process_running(name: str) -> bool:
    """Checks whether a process of the same name is running

    Args:
        name (str)

    Returns:
        bool
    """
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"] == name:
            return True
    return False


def _start_emulator() -> None:
    path = settings.app_settings["emulator_path"]
    if (
        path
        and os.path.exists(path)
        and not _is_process_running(os.path.split(path)[1])
    ):
        logger.info("Starting emulator...")
        subprocess.Popen(path)


def _start_adb_server() -> None:
    adb_path = os.path.join(project_dir, "adb")
    logger.debug(f"Using adb at {adb_path}")

    logger.debug("Starting adb server...")
    subprocess.run([adb_path, "start-server"])

    def kill_adb_server() -> None:
        subprocess.run([adb_path, "kill-server"])

    # atexit.register(kill_adb_server)


def _is_correct_resolution(dims: tuple[int, int]) -> bool:
    return dims == RESOLUTION or dims == RESOLUTION[::-1]


def _check_device_resolution() -> None:
    DISCLAIMER = "Other resolutions may result in poor detection"

    logger.debug("Checking resolution...")

    display = adb_client.getPhysicalDisplayInfo()
    w = display["width"]
    h = display["height"]
    d = display["density"]

    if not _is_correct_resolution((w, h)):
        logger.warning(
            f"Unsupported resolution {w}x{h}. Please change your resolution to "
            + f"{RESOLUTION[0]}x{RESOLUTION[1]}. {DISCLAIMER}"
        )
    if d != DPI:
        logger.warning(
            f"Unsupported DPI {d}. Please change your DPI to {DPI}. {DISCLAIMER}"
        )


def _run_game() -> None:
    logger.debug("Running game...")
    adb_client.shell("monkey -p com.lilithgame.hgame.gp 1")


# Waits until the campaign_selected button is visible. While it isn't, try to recover.
def _wait_until_game_active() -> None:
    # Long so patching etc doesn't lead to timeout
    TIMEOUT_S = 60

    logger.debug("Searching for Campaign screen..")
    # TODO: Only start recovering here after the game is loaded
    reset_to_screen(seconds=1, tries=TIMEOUT_S)
    logger.info("Game loaded!")


def expand_menus() -> None:
    """Expands the left and right game menus"""
    touch_img_while_visible("buttons/downarrow", confidence=0.8, tries=3)


## Control


def wait(seconds=1) -> None:
    """Sleeps for a time, taking into account the wait multiplier

    Args:
        seconds (int, optional): seconds to sleep for. Defaults to 1.
    """
    time.sleep(settings.app_settings["wait_multiplier"] * seconds)


def touch_xy(x: int, y: int) -> None:
    TOUCH_DURATION_MS = 10
    adb_client.longTouch(x, y, TOUCH_DURATION_MS)


def touch_xy_wait(*args, seconds=1) -> None:
    touch_xy(*args)
    wait(seconds)


def drag(start: tuple[int, int], end: tuple[int, int], duration=100) -> None:
    adb_client.drag(start, end, duration)


def drag_wait(*args, seconds=1, **kwargs):
    drag(*args, **kwargs)
    wait(seconds)


def get_frame() -> Image:
    """Gets the last frame streamed from scrcpy

    If the frame is not 1080x1920, then it is resized.

    Returns:
        PIL.Image
    """
    im = Image.fromarray(scrcpy_client.last_frame[:, :, ::-1])
    if not _is_correct_resolution(im.size):
        im = im.resize(RESOLUTION)
    return im


# Saves screenshot locally
def save_scrcpy_screenshot(name) -> None:
    image = get_frame()
    # Convert image back to bytearray
    byteIO = io.BytesIO()
    image.save(byteIO, format="PNG")
    image = byteIO.getvalue()
    with open(name + ".png", "wb") as f:
        f.write(image)


# Checks the pixel at the XY coordinates
# C Variable is array from 0 to 2 for RGB value
def check_pixel(x: int, y: int, c):
    im = get_frame()
    screenshot = numpy.asarray(im)  # Make it an array
    return screenshot[y, x, c]


def open_image(rel_path: str) -> Image:
    return Image.open(os.path.join(SRC_DIR, "img", rel_path))


def locate_img(
    image: str,
    region=(0, 0, RESOLUTION[0], RESOLUTION[1]),
    confidence=0.9,
    retry=1,
    grayscale: None | bool = None,
):
    for i in range(retry):
        box = pyscreeze.locate(
            open_image(f"{image}.png"),
            get_frame(),
            region=region,
            confidence=confidence,
            grayscale=grayscale,
        )
        if box:
            break
        if i != retry - 1:
            wait()

    return box


def wait_until_img_visible(
    image: str,
    region=(0, 0, RESOLUTION[0], RESOLUTION[1]),
    confidence=0.9,
    timeout_s=30,
    grayscale: None | bool = None,
):
    """Waits until an image is visible

    Polls to check whether the image is visible every 0.1s.

    Args:
        image (str): image name
        region (tuple, optional): See `pyscreeze.locate`. Defaults to (0, 0, RESOLUTION[0], RESOLUTION[1]).
        confidence (float, optional): See `pyscreeze.locate`. Defaults to 0.9.
        timeout_s (int, optional): timeout in seconds. Defaults to 30.
        grayscale (bool, optional): See `pyscreeze.locate`. Defaults to False.

    Returns:
        None | pyscreeze.Box: See `pyscreeze.locate`
    """
    # TODO: Update to be a multiple of the scrcpy max framerate
    POLLING_INTERVAL_S = 0.1

    for i in range(math.floor(timeout_s / POLLING_INTERVAL_S)):
        box = locate_img(image, region, confidence, grayscale=grayscale)
        if box:
            logger.debug(f"{image} available after {i * POLLING_INTERVAL_S}s")
            break
        wait(POLLING_INTERVAL_S)

    return box


def touch_box(box: pyscreeze.Box) -> None:
    x, y, w, h = box
    x_center = round(x + w / 2)
    y_center = round(y + h / 2)
    touch_xy(x_center, y_center)


# Makes us seem a little more human, if you're into that ;) (at the expense of speed)
def touch_img_when_visible_after_wait(*args, seconds=1, **kwargs):
    box = wait_until_img_visible(*args, **kwargs)
    if box:
        wait(seconds)
        touch_box(box)
    return bool(box)


def touch_img_when_visible(*args, **kwargs) -> bool:
    return touch_img_when_visible_after_wait(*args, seconds=0, **kwargs)


# Seconds is time to wait after touch_img_waiting the image
# Retry will try and find the image x number of times, useful for animated or covered buttons, or to make sure the button is not skipped
# Suppress will disable warnings, sometimes we don't need to know if a button isn't found
def touch_img_wait(
    image: str,
    region=(0, 0, RESOLUTION[0], RESOLUTION[1]),
    confidence=0.9,
    seconds=1,
    retry=1,
    grayscale: None | bool = None,
) -> bool:
    box = locate_img(image, region, confidence, retry, grayscale)
    if not box:
        logger.debug(f"{image} not found")
    else:
        touch_box(box)
        wait(seconds)
    return bool(box)


def touch_img_while_other_visible(
    image: str,
    other: str,
    region=(0, 0, RESOLUTION[0], RESOLUTION[1]),
    other_region=(0, 0, RESOLUTION[0], RESOLUTION[1]),
    confidence=0.9,
    seconds=1,
    tries=5,
):
    for _ in range(tries):
        if not locate_img(other, other_region, confidence):
            break
        touch_img_wait(image, region, confidence, seconds)
    else:
        logger.error(
            f"Kept tapping image {image}, but image {other} was still visible "
            + f"after {tries} tries each {seconds} seconds apart"
        )
        return False

    return True


def touch_img_while_visible(
    image, region=(0, 0, 1080, 1920), confidence=0.9, seconds=1, tries=5
):
    # Touching an image while it is visible is a special case of touching it
    # while an arbitrary image is visible
    return touch_img_while_other_visible(
        image, image, region, region, confidence, seconds, tries
    )


## Util


# Checks the 5 locations we find arena battle buttons in and selects the based on choice parameter
# If the choice is outside the found buttons we return the last button found
# if HoE is true we just check the blue pixel value for the 5 buttons
def select_opponent(choice, seconds=1, hoe=False) -> None | bool:
    screenshot = get_frame()
    search = open_image(os.path.join("buttons", "arenafight.png"))

    if hoe is False:  # Arena
        locations = {
            (715, 650, 230, 130),
            (715, 830, 230, 130),
            (715, 1000, 230, 130),
            (715, 1180, 230, 130),
            (715, 1360, 230, 130),
        }  # 5 regions for the buttons
    else:  # HoE
        locations = {
            (850, 680),
            (850, 840),
            (850, 1000),
            (850, 1160),
            (850, 1320),
        }  # 5 regions for the buttons
    battleButtons = []

    # Check each location and add Y coordinate to array (as X doesnt change we don't need it)
    for loc in locations:
        if hoe is False:
            res = pyscreeze.locate(search, screenshot, confidence=0.9, region=loc)
            if res != None:
                battleButtons.append(
                    loc[1] + (loc[3] / 2)
                )  # Half the height so we have the middle of the button
        else:
            res = check_pixel(loc[0], loc[1], 2)  # Check blue pixel value
            logger.debug(f"Pixel blue value for {loc} is {res}")
            if res > 150:  # If the blue value is more than 150 we have a button
                battleButtons.append(
                    loc[1]
                )  # Append Y coord as X is static (also I can't work out how to sort with both)
    battleButtons.sort()  # sort results from top to bottom

    if len(battleButtons) == 0:
        logger.error("No opponents found!")
        return

    if choice > len(
        battleButtons
    ):  # If the choice is higher than the amount of results we take the last result in the list
        touch_xy_wait(820, battleButtons[len(battleButtons) - 1])
        wait(seconds)
        return True
    else:
        touch_xy_wait(820, battleButtons[choice - 1])
        wait(seconds)
        return True


# Scans the coordinates from the two arrays, if a 'Dispatch' button is found returns the X and Y of the center of the button as an array
# We have two arrays as when we scroll down in the bounty list the buttons are offset compared to the unscrolled list
def get_dispatch_btns(scrolled=False) -> list[tuple[int, int]]:
    screenshot = get_frame()
    search = open_image(os.path.join("buttons", "dispatch_bounties.png"))
    locations = {
        (820, 430, 170, 120),
        (820, 650, 170, 120),
        (820, 860, 170, 120),
        (820, 1070, 170, 120),
        (820, 1280, 170, 120),
    }  # Location of the first 5 buttons
    locations_scrolled = {
        (820, 460, 170, 160),
        (820, 670, 170, 160),
        (820, 880, 170, 160),
        (820, 1090, 170, 160),
        (820, 1300, 170, 160),
    }  # Location of the first 5 buttons after scrolling down
    dispatchButtons = []
    wait()

    # Different locations if we scrolled down
    if scrolled is True:
        locations = locations_scrolled
    # Check each location and add Y coordinate to array (as X doesnt change we don't need it)
    for loc in locations:
        res = pyscreeze.locate(search, screenshot, confidence=0.9, region=loc)
        if res != None:
            dispatchButtons.append(
                round(loc[1] + (loc[3] / 2))
            )  # Half the height so we have the middle of the button

    dispatchButtons.sort()
    return dispatchButtons


def touch_escape_wait(seconds=1) -> None:
    """Touches a neutral location that should not be a button

    Args:
        seconds (int, optional): passed to `touch_xy_wait`. Defaults to 1.
    """
    touch_xy_wait(300, 50, seconds=seconds)  # maybe x=420 is better :)


class Screen(enum.Enum):
    CAMPAIGN = "campaign"
    DARK_FOREST = "darkforest"
    RANHORN = "ranhorn"


SCREEN_REGIONS: dict[Screen, tuple[int, int, int, int]] = {
    "campaign": (424, 1750, 232, 170),
    "darkforest": (208, 1750, 226, 170),
    "ranhorn": (0, 1750, 210, 160),
}


def is_screen(screen: Screen) -> bool:
    return bool(
        locate_img(
            f"buttons/{screen.value}_selected", SCREEN_REGIONS[screen.value], 0.8
        )
    )


def go_to_screen(screen: Screen):
    return touch_img_wait(
        f"buttons/{screen.value}_unselected", SCREEN_REGIONS[screen.value]
    )


def reset_to_screen(screen=Screen.CAMPAIGN, seconds=1, tries=8) -> None:
    """Navigates back to the base state, the Campaign screen

    Args:
        tries (int, optional): tries before deeming things unrecoverable and
            exiting. Defaults to 8.
    """

    def after_actions():
        # Click in case we found Campaign in the background (basically if a
        # campaign attempt fails)
        if screen is Screen.CAMPAIGN:
            touch_xy_wait(550, 1900)
        expand_menus()

    # If we don't need to recover and can go to the screen peacefully, do that
    # Don't need to recover = starting on one of the screens in a good state
    go_to_screen(screen)
    if is_screen(screen):
        after_actions()
        return

    for i in range(tries):
        # Gun through all the buttons that can help us get out
        logger.debug(f"Recovery attempt {i + 1}")

        # General escape
        touch_escape_wait()

        # If any of these escapes exist, tap one of them
        (
            touch_img_wait("buttons/back", (0, 1500, 250, 419))
            or touch_img_wait("buttons/back_narrow", (0, 1500, 250, 419))
            or touch_img_wait("buttons/exit", (578, 1250, 290, 88))
            or touch_img_wait("buttons/exitmenu", (700, 0, 379, 500))
            or touch_img_wait("buttons/exitmenu_trial", (700, 0, 379, 500))
        )

        # If there is a confirmation, tap it
        (
            touch_img_wait("buttons/confirm_small")  # (200, 750, 600, 649)
            or touch_img_wait("buttons/confirm_stageexit", (200, 750, 600, 649))
        )

        go_to_screen(screen)
        if is_screen(screen):
            after_actions()
            break
        if i != tries - 1:
            wait(seconds)
    else:
        logger.error("Recovery failed, exiting")
        exit(0)

    logger.info("Recovered successfully")
