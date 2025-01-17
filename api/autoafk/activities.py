from datetime import datetime
from typing import Callable, TypedDict

from autoafk import settings as app_settings_h
from autoafk.logger import logger
from autoafk.thread_state import handle_pause_and_stop_events
from autoafk.tools import (
    check_pixel,
    drag_wait,
    expand_menus,
    get_dispatch_btns,
    locate_img,
    reset_to_screen,
    Screen,
    select_opponent,
    touch_escape,
    touch_escape_after_wait,
    touch_escape_wait,
    touch_img,
    touch_img_wait,
    touch_img_when_visible,
    touch_img_when_visible_after_wait,
    touch_img_when_visible_while_visible,
    touch_xy,
    touch_xy_after_wait,
    touch_xy_wait,
    wait,
    wait_until_img_visible,
)


REGIONS = {
    "autobattle0": (562, 994, 144, 122),
}


def collect_afk_rewards() -> None:
    logger.info("Collecting AFK rewards...")
    reset_to_screen()

    touch_xy_after_wait(550, 1550, seconds=0.1)
    touch_img_when_visible("buttons/collect")
    logger.info("AFK rewards collected!")

    touch_escape_after_wait()  # In case we level up
    touch_img_when_visible("labels/tap-anywhere-to-close", timeout_s=3)


def collect_mail() -> None:
    logger.info("Collecting mail...")
    reset_to_screen()

    touch_img_when_visible("buttons/mail")
    touch_img_when_visible("buttons/collect_all")
    logger.info("Mail collected!")

    # Note that if there is no mail we only need to escape once (no rewards)
    touch_escape_after_wait(0.1)  # Clear rewards
    touch_escape_after_wait(0.1)  # Exit


def send_and_receive_companion_points(mercs=False) -> None:
    logger.info("Sending/receiving companion points...")
    reset_to_screen()

    touch_img_when_visible("buttons/friends")
    touch_img_when_visible("buttons/sendandreceive")
    logger.info("Companion points sent/received")

    if mercs:
        logger.info("Lending out mercs...")
        touch_xy_wait(720, 1760)  # Short term
        touch_xy_wait(990, 190)  # Manage
        touch_xy_wait(630, 1590)  # Apply
        touch_xy_wait(750, 1410)  # Auto lend
        touch_img_wait("buttons/exitmenu")
        logger.info("Mercenaries lent out")

    touch_img_when_visible_after_wait("buttons/back", seconds=0.25)


class CollectFastRewardsSettings(TypedDict):
    times: int


def collect_fast_rewards(settings: CollectFastRewardsSettings) -> None:
    t = settings["times"]
    logger.info(f"Collecting fast rewards {t} times...")
    reset_to_screen()

    # Check whether the pixel where the notification dot is has a high enough red value
    wait_until_img_visible("buttons/fastrewards")
    if not check_pixel(980, 1620, 0) > 220:
        logger.warning("Fast Rewards already collected")
        return

    touch_img("buttons/fastrewards")
    for _ in range(settings["times"]):
        touch_xy_after_wait(710, 1260)  # Button changes depending on use
        touch_escape_after_wait()  # Clear rewards
    logger.info("Fast rewards collected")

    touch_img_when_visible("buttons/close")


# Loads and exits a campaign abttle for dailies quest
def attempt_campaign() -> None:
    logger.info("Attempting campaign battle...")
    reset_to_screen()

    open_campaign()

    # Begin button is 'beginbattle' for multis and 'begin' for singles, so we
    # use location
    wait_until_img_visible("buttons/formations")
    touch_xy(700, 1850)
    logger.info("Campaign battle attempted")

    touch_img_when_visible("buttons/pause")
    touch_img_when_visible("buttons/exitbattle")
    touch_img_when_visible("buttons/back", timeout_s=3)


class SoloBountySettings(TypedDict):
    dust: bool
    diamonds: bool
    juice: bool
    shards: bool


class DispatchSoloBountiesSettings(SoloBountySettings):
    max_refreshes: int
    number_remaining_to_dispatch_all: int


class DispatchBountiesSettings(DispatchSoloBountiesSettings):
    event_bounties: bool
    solo_bounties: bool
    team_bounties: bool


def dispatch_bounties(settings: DispatchBountiesSettings) -> None:
    logger.info("Dispatching bounties...")
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy_after_wait(600, 1320, seconds=0.1)

    wait_until_img_visible("labels/bountyboard")

    if settings["solo_bounties"]:
        touch_xy(650, 1700)  # Solo tab
        touch_img_when_visible_after_wait(
            "buttons/collect_all", timeout_s=1, seconds=0.1
        )
        dispatch_solo_bounties(settings)

    if settings["team_bounties"]:
        touch_xy_after_wait(950, 1700, seconds=0.1)  # Team tab
        touch_img_when_visible("buttons/collect_all", timeout_s=1)
        touch_img_when_visible("buttons/dispatch")
        touch_img_when_visible("buttons/confirm")

    if settings["event_bounties"] and touch_img_when_visible(
        "labels/event_bounty", timeout_s=0.1
    ):
        touch_img_when_visible("buttons/collect_all", timeout_s=1)
        while touch_img_when_visible_after_wait(
            "buttons/dispatch_bounties", timeout_s=1, seconds=0.1
        ):
            touch_xy_after_wait(530, 1030, seconds=0.25)
            touch_xy_after_wait(120, 1500, seconds=0.25)
            touch_img_when_visible("buttons/dispatch")

    logger.info("Bounties dispatched")

    touch_img_when_visible("buttons/back")


# Loops through the bounty board returning found Dispatch buttons for dispatcher() to handle
# maxrefreshes is how many times to refresh before hitting dispatch all
# remaining is how many leftover bounties we should use dispatch all on rather than refresh again
def dispatch_solo_bounties(settings: DispatchSoloBountiesSettings) -> None:
    for i in range(settings["max_refreshes"] + 1):
        # Send the list to the function to dispatch
        dispatcher(get_dispatch_btns(), settings)
        drag_wait((550, 800), (550, 500), duration=200, seconds=2)  # scroll down
        dispatcher(get_dispatch_btns(scrolled=True), settings)

        if (
            len(get_dispatch_btns(scrolled=True))
            <= settings["number_remaining_to_dispatch_all"]
        ):
            t = settings["number_remaining_to_dispatch_all"]
            logger.info(f"{t} or less bounties remaining, dispatching...")
            break

        if i != settings["max_refreshes"]:
            touch_img_when_visible("buttons/refresh")
            touch_img_when_visible("buttons/confirm")
    else:
        t = settings["max_refreshes"]
        logger.info(f"{t} refreshes done, dispatching remaining...")

    touch_img_wait("buttons/dispatch", confidence=0.8, grayscale=True)
    touch_img_wait("buttons/confirm")


# Recieves a list of Dispatch buttons Y coordinates and checks/dispatches the resource
def dispatcher(dispatches, settings: SoloBountySettings) -> None:
    # Names and Buttons
    bounty_types = {
        "dust": "labels/bounties/dust",
        "diamonds": "labels/bounties/diamonds",
        "juice": "labels/bounties/juice",
        "shards": "labels/bounties/shards",
        # "gold": "labels/bounties/gold",
        # "soulstone": "labels/bounties/soulstone",
    }

    # For loop over each button passed to the function
    for button in dispatches:
        for resource, image in bounty_types.items():
            # For each button we use `region=` to only check the resource in bounds to the left of it
            # There are no settings for gold or soulstones
            if settings[resource] and locate_img(image, (30, button - 100, 140, 160)):
                logger.info(f"Dispatching {resource}")
                touch_xy_wait(900, button)
                touch_xy_wait(350, 1150)
                touch_xy_wait(750, 1150)
                break  # done processing this dispatch button


class ChallengeSettings(TypedDict):
    battles: int


class ChallengeOpponentSettings(ChallengeSettings):
    opponent_number: int


def challenge_arena(settings: ChallengeOpponentSettings) -> None:
    t = settings["battles"]
    logger.info(f"Battling Arena of Heroes {t} times")
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy_wait(740, 1050)
    touch_xy_wait(550, 50)

    if not touch_img_wait(
        "labels/arenaofheroes_new"
    ):  # The label font changes for reasons
        logger.error("Arena of Heroes not found, attempting to recover")
        reset_to_screen(Screen.DARK_FOREST)
        return

    # retries for animated button
    touch_img_wait("buttons/challenge", retry=3)

    for i in range(settings["battles"]):
        select_opponent(choice=settings["opponent_number"])
        # This is rather than Battle button as that is animated and hard to read
        while locate_img("buttons/heroclassselect", retry=3):
            touch_xy_wait(550, 1800)
        # Retries as ulting heros can cover the button
        touch_img_wait("buttons/skip", retry=5)
        if get_battle_results(type="arena"):
            logger.info(f"Battle #{i + 1} victory!")
            touch_xy_wait(600, 550)  # Clear loot popup
        else:
            logger.error(f"Battle #{i + 1} defeat!")
        touch_xy_wait(600, 550)  # Back to opponent selection

        handle_pause_and_stop_events()

    logger.info("Arena battles completed")

    touch_img_wait("buttons/exitmenu")
    touch_img_wait("buttons/back", retry=3)
    touch_img_wait("buttons/back", retry=3)


def collect_gladiator_coins() -> None:
    logger.info("Collecting gladiator coins...")
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy_wait(740, 1050)
    touch_xy_wait(550, 50)
    drag_wait((550, 800), (550, 500), duration=200, seconds=2)  # scroll down

    # The label font changes for reasons
    if not touch_img_wait("labels/legendstournament_new"):
        logger.error("Legends Tournament not found")
        reset_to_screen(Screen.DARK_FOREST)
        return

    touch_xy_wait(550, 300, seconds=2)
    touch_xy_wait(50, 1850)
    logger.info("Gladiator coins collected")

    touch_img_wait("buttons/back")
    touch_img_wait("buttons/back")


def use_bag_consumables() -> None:
    logger.info("Using bag consumables...")

    if not touch_img_when_visible("menus/bag"):
        logger.error("Bag not found, attempting to recover")
        reset_to_screen()
        return

    touch_img_wait("buttons/batchselect", retry=3)

    if locate_img("buttons/confirm_grey"):
        logger.warning("Nothing selected/available! Returning...")
        touch_img_wait("buttons/back")
        return

    touch_xy_wait(550, 1650, seconds=2)

    crash_counter = 0  # So we don't get stuck forever in the Use button loop
    while not locate_img("buttons/use_batch"):
        touch_xy_wait(550, 1800)

        crash_counter += 1
        if crash_counter > 30:
            logger.error(
                "Something went wrong (normally gear chests being selected), returning..."
            )
            touch_img_wait("buttons/back")
            touch_img_wait("buttons/back")
            return

    touch_xy_wait(550, 1800)  # Use
    touch_xy_wait(950, 1700)  # 'All' Bag button to clear loot
    logger.info("Bag consumables used")

    touch_img_wait("buttons/back")


# TODO Get image for the fire debuff banner
def collect_ts_rewards() -> None:
    logger.info("Collecting daily TS loot...")
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy_wait(740, 1050)  # open Arena of Heroes
    touch_xy_wait(550, 50)  # Clear Arena Tickets

    ts_banners = [
        "labels/tsbanner_forest",
        "labels/tsbanner_ice",
        "labels/tsbanner_fog",
        "labels/tsbanner_volcano",
    ]
    for banner in ts_banners:  # Check the 4 debuffs
        if touch_img_wait(banner, seconds=2):
            if touch_img_wait("buttons/ts_path"):
                touch_xy_wait(370, 945)  # Choose path
                touch_xy_wait(520, 1700)  # Confirm path
                touch_img_wait("buttons/back", retry=3)
                touch_img_wait("buttons/back", retry=3)
            else:
                touch_xy_wait(400, 50, seconds=2)  # Clear Rank Up
                touch_xy_wait(400, 50, seconds=2)  # Clear Loot
                touch_img_wait("buttons/back", retry=3)
                touch_img_wait("buttons/back", retry=3)
                logger.info("    Treasure Scramble daily loot collected!")
            break
    else:
        logger.error("Treasure Scramble not found")
        reset_to_screen(Screen.DARK_FOREST)


def collect_fountain_of_time() -> None:
    logger.info("Collecting Fountain of Time...")
    reset_to_screen(Screen.DARK_FOREST)

    touch_img_when_visible("buildings/trift")

    if not wait_until_img_visible("labels/temporalrift"):
        logger.error("Temporal Rift not found")
        reset_to_screen(Screen.DARK_FOREST)
        return

    touch_xy_wait(550, 1800)
    touch_xy_wait(250, 1300)
    touch_xy_wait(700, 1350)  # Collect
    touch_xy_wait(550, 1800, seconds=3)  # Clear level up
    touch_xy_wait(550, 1800, seconds=3)  # Clear limited deal
    touch_xy_wait(550, 1800, seconds=3)  # Clear newly unlocked
    logger.info("Fountain of Time collected")

    touch_img_when_visible("buttons/back")


class PushSettings(TypedDict):
    formation: int


def run_autobattle(settings: PushSettings, open_mode: Callable[[], None]) -> None:
    app_settings = app_settings_h.app_settings

    open_mode()

    config_battle_formation(settings)
    touch_img_when_visible("buttons/autobattle")
    touch_img_when_visible("buttons/activate")
    while True:
        wait(app_settings["victory_check_freq_min"] * 60)

        # If a spam popup previously showed up, then it will reappear inside of
        # autobattle after beating the next battle.
        #
        # For campaign, this will stop the battling even with autobattle still
        # active. When exiting to clear it, we fall out of the mode to the main
        # screen.
        #
        # For tower, it doesn't stop the battling and we don't fall out. Clear
        # it anyway if we happen to see it in the background.
        #
        # To handle both of these cases no matter where we stop, do a full reset
        # and reopen.
        is_spam = locate_img("labels/tap-anywhere-to-close")
        if is_spam:
            reset_to_screen()

            open_mode()

            config_battle_formation(settings)
            touch_img_when_visible("buttons/autobattle")
            touch_img_when_visible("buttons/activate")
            continue

        # Make sure we are checking for victory at a well-known time so we don't
        # get caught in a weird state. Choose right when a battle starts. If the
        # team goes down instantly than we are still in trouble, but that should
        # never happen using winning formations unless we don't have a build, in
        # which case we are stuck anyway.
        wait_until_img_visible("buttons/autobattle")
        wait_until_img_visible("buttons/pause")
        touch_escape()
        is_status_open = wait_until_img_visible("buttons/cancel", timeout_s=0.5)
        # Sometimes the menu doesn't open, about a 2% chance. Since it is rare
        # just take another wait before checking.
        if not is_status_open:
            continue

        # If we see 0 then we haven't won
        is_defeat = locate_img("labels/autobattle_0", REGIONS["autobattle0"])
        if is_defeat:
            if not app_settings["surpress_victory_check_spam"]:
                t = app_settings["victory_check_freq_min"]
                logger.info(f"No victory found, checking again in {t} minutes.")

            touch_img("buttons/cancel")
        # Otherwise assume victory. Go back to hero select, clear victory
        # popups, load the formation for the current stage, and resume.
        else:
            t = settings["formation"]
            logger.info(
                f"Victory found! Loading the {t} formation for the current stage.."
            )

            touch_img("buttons/exit")
            touch_img_when_visible("buttons/pause")
            touch_img_when_visible("buttons/tryagain")

            # Clear popup spam. These episodes occur about every 20 stages.
            # For campaign, they show up here.
            touch_img_when_visible("labels/tap-anywhere-to-close", timeout_s=3)

            config_battle_formation(settings)

            # Annoyingly, for tower, they show up here.
            touch_img_when_visible("labels/tap-anywhere-to-close", timeout_s=3)

            touch_img_when_visible("buttons/autobattle")
            touch_img_when_visible("buttons/activate")

        # TODO: This should be more responsive, check it more often than when
        # checking for victories
        handle_pause_and_stop_events()


def open_tower(tower: str) -> None:
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy(500, 870)
    wait_until_img_visible("labels/kingstower")
    wait()

    TOWER_LOCATIONS = {
        "King's Tower": [500, 870],
        "Lightbearer Tower": [300, 1000],
        "Wilder Tower": [800, 600],
        "Mauler Tower": [400, 1200],
        "Graveborn Tower": [800, 1200],
        "Hypogean Tower": [600, 1500],
        "Celestial Tower": [300, 500],
    }
    loc = TOWER_LOCATIONS[tower]
    touch_xy_wait(loc[0], loc[1])

    touch_img_when_visible_after_wait("buttons/challenge_plain", seconds=0.1)


# TODO: Add a stop after x duration feature or similar
# stop after no victory for x duration
def push_tower(tower: str, settings: PushSettings) -> None:
    logger.info(f"Pushing {tower}...")
    reset_to_screen(Screen.DARK_FOREST)

    run_autobattle(settings, open_mode=lambda: open_tower(tower))


def push_kt(settings: PushSettings) -> None:
    push_tower("King's Tower", settings)


def push_lb_tower(settings: PushSettings) -> None:
    push_tower("Lightbearer Tower", settings)


def push_mauler_tower(settings: PushSettings) -> None:
    push_tower("Mauler Tower", settings)


def push_wilder_tower(settings: PushSettings) -> None:
    push_tower("Wilder Tower", settings)


def push_gb_tower(settings: PushSettings) -> None:
    push_tower("Graveborn Tower", settings)


def push_cele_tower(settings: PushSettings) -> None:
    push_tower("Celestial Tower", settings)


def push_hypo_tower(settings: PushSettings) -> None:
    push_tower("Hypogean Tower", settings)


def open_campaign() -> None:
    # might need to wait some, its heavily animated
    touch_img_when_visible("buttons/begin")
    # now maybe 2 are visible, constrain with a region
    touch_img_when_visible("buttons/begin_plain", timeout_s=1)


def push_campaign(settings: PushSettings) -> None:
    logger.info("Pushing campaign...")
    reset_to_screen()

    run_autobattle(settings, open_mode=open_campaign)


def config_battle_formation(settings: PushSettings) -> None:
    app_settings = app_settings_h.app_settings

    if app_settings["ignore_formations"]:
        logger.warning("Ignore formations is enabled, skipping formation selection...")
        return

    # Select formation
    touch_img_when_visible("buttons/formations")
    if app_settings["use_popular_formations"]:
        touch_img_when_visible("labels/popular-formations")
        wait_until_img_visible("labels/popular-formations-following")
    wait_until_img_visible("buttons/formation_select")
    touch_xy(850, 425 + (settings["formation"] * 175))
    touch_img_when_visible("buttons/use")
    wait_until_img_visible("buttons/confirm_small")

    # Configure artifacts
    artifacts_region = (230, 1100, 80, 80)
    use_artifacts = locate_img("buttons/checkbox_checked", artifacts_region)
    if bool(use_artifacts) != settings["copy_artifacts"]:
        if not use_artifacts:
            next_state = "buttons/checkbox_checked"
            next_text = "Enabling"
        else:
            next_state = "buttons/checkbox_blank"
            next_text = "Disabling"
        logger.info(f"{next_text} artifact copying...")
        touch_xy(275, 1150)
        wait_until_img_visible(next_state, artifacts_region)

    touch_img("buttons/confirm_small")


def attempt_kt() -> None:
    logger.info("Attempting Kings Tower battle...")
    reset_to_screen(Screen.DARK_FOREST)

    open_tower("King's Tower")

    # For reasons sometimes this button is 'beginbattle' and sometimes it is
    # 'begin', so we use location
    wait_until_img_visible("buttons/formations")
    touch_xy(700, 1850)
    touch_img_when_visible("buttons/pause")
    touch_img_when_visible("buttons/exitbattle")
    touch_img_when_visible_while_visible("buttons/back", seconds=0.25)

    logger.info("Tower attempted successfully")


def collect_inn_gifts() -> None:
    logger.info("Collecting Inn gifts...")
    reset_to_screen(Screen.RANHORN)

    touch_xy_wait(500, 200, seconds=4)

    if not locate_img("buttons/manage"):
        logger.error("Inn not found")
        reset_to_screen(Screen.RANHORN)
        return

    for i in range(3):  # ???
        if touch_img_wait("buttons/inn_gift", seconds=2):
            touch_xy_wait(550, 1400, seconds=0.5)  # Clear loot
            touch_xy_wait(550, 1400, seconds=0.5)  # Clear loot

    logger.info("Inn Gifts collected.")

    # wait before next task as loading ranhorn can be slow
    touch_img_wait("buttons/back", seconds=2)


class MakeStorePurchasesSettings(TypedDict):
    times: int
    quick_buy: bool
    gold__shards: bool
    gold__dust: bool
    gold__silver_emblems: bool
    gold__emblems: bool
    gold__poe: bool
    diamonds__timegazer: bool
    diamonds__staffs: bool
    diamonds__baits: bool
    diamonds__cores: bool
    diamonds__dust: bool
    diamonds__elite_soulstone: bool
    diamonds__superb_soulstone: bool


def make_store_purchases_h(counter, settings: MakeStorePurchasesSettings) -> None:
    toprow = {
        "diamonds__staffs": [180, 920],
        "diamonds__cores": [425, 920],
        "diamonds__timegazer": [650, 920],
        "diamonds__baits": [875, 920],
    }
    bottomrow = {
        "gold__dust": "buttons/shop/dust",
        "gold__shards": "buttons/shop/shards_gold",
        "diamonds__dust": "buttons/shop/dust_diamonds",
        "diamonds__elite_soulstone": "buttons/shop/soulstone",
        "diamonds__superb_soulstone": "buttons/shop/superstone",
        "gold__silver_emblem": "buttons/shop/silver_emblems",
        "gold__gold_emblem": "buttons/shop/gold_emblems",
        "gold__poe": "buttons/shop/poe",
    }

    # Prettify the names were outputting into console
    item_name_map = {
        "diamonds__staffs": "Arcane Staffs",
        "diamonds__cores": "Elemental Cores",
        "diamonds__timegazer": "Timegazer Card",
        "diamonds__baits": "Bait",
        "gold__dust": "Dust (Gold)",
        "gold__shards": "Shards",
        "diamonds__dust": "Dust (Diamonds)",
        "diamonds__elite_soulstone": "Elite Soulstone",
        "diamonds__superb_soulstone": "Superb Soulstone",
        "gold__silver_emblem": "Silver Emblems",
        "gold__gold_emblem": "Gold Emblems",
        "gold__poe": "Poe Coins (Gold)",
    }

    # Purchase top row
    for item, pos in toprow.items():
        if settings[item]:
            if item == "diamonds__timegazer" and counter > 0:  # only one TG card
                continue
            if item == "diamonds__baits" and counter > 1:  # only two baits
                continue
            if (
                item == "diamonds__cores" or item == "diamonds__staffs"
            ) and counter > 2:  # only three shards/staffs
                continue
            logger.info("    Buying: " + item_name_map[item])
            touch_xy_wait(pos[0], pos[1])
            touch_img_wait("buttons/shop/purchase")
            touch_xy_wait(550, 1220, seconds=2)

    # Scroll down so bottom row is visible
    drag_wait((550, 1500), (550, 1200), 500, seconds=5)

    # Purchase bottom 4 rows
    for item, button in bottomrow.items():
        if settings[item]:
            if touch_img_wait(button, confidence=0.95):
                logger.info("Buying: " + item_name_map[item])
                touch_img_wait("buttons/shop/purchase")
                touch_xy_wait(550, 1220)

    # Long wait else Twisted Realm isn't found after if enabled in Dailies
    wait(3)


def make_store_purchases(settings: MakeStorePurchasesSettings, skipQuick=0) -> None:
    is_quick_buy = settings["quick_buy"] and skipQuick == 0
    buy_type = "quick buy" if is_quick_buy else "purchase"
    t = settings["times"]
    logger.info(f"Making {t} store {buy_type}s...")
    reset_to_screen(Screen.RANHORN)

    touch_img_when_visible("buildings/store")

    if not wait_until_img_visible("labels/store"):
        logger.error("Store not found, attempting to recover")
        reset_to_screen(Screen.RANHORN)
        return

    if is_quick_buy:
        make_store_purchases_quick(settings)
    else:
        i = 1
        # First purchases
        make_store_purchases_h(i, settings)
        # refresh purchases
        while i < settings["times"]:
            touch_xy_wait(1000, 300)
            touch_img_wait("buttons/confirm", seconds=5)
            i += 1
            logger.info("Refreshed store {i} times.")
            make_store_purchases_h(i, settings)

    logger.info("Store purchases complete")

    touch_img_when_visible("buttons/back")


def make_store_purchases_quick(settings: MakeStorePurchasesSettings) -> None:
    if not touch_img_wait("buttons/quickbuy", seconds=2):
        logger.info("Quickbuy not found, switching to old style")
        touch_img_wait("buttons/back")
        make_store_purchases(settings, 1)
    else:
        touch_img_wait("buttons/purchase", seconds=5)
        touch_xy_wait(970, 90, seconds=2)
        counter = 1
        while counter < settings["times"]:
            touch_xy_wait(1000, 300)
            touch_img_wait("buttons/confirm", seconds=2)
            touch_img_wait("buttons/quickbuy", seconds=2)
            touch_img_wait("buttons/purchase", seconds=2)
            touch_xy_wait(970, 90)
            counter += 1


def battle_guild_hunts() -> None:
    logger.info("Battling guild hunts...")
    reset_to_screen(Screen.RANHORN)

    touch_xy_wait(380, 360, seconds=6)
    touch_xy_wait(550, 1800)  # Clear chests
    # Collect any guild reward chests we have
    touch_img_wait("buttons/guild_chests", seconds=2)
    if touch_img_wait("buttons/collect_guildchest"):
        touch_xy_wait(550, 1300)
        touch_xy_wait(900, 550)
        touch_xy_wait(550, 1800, seconds=2)  # Clear window
    else:
        touch_xy_wait(550, 1800)  # Clear window
    touch_xy_wait(290, 860)

    if not locate_img("labels/wrizz"):
        logger.error("Error opening guild hunts")
        reset_to_screen(Screen.RANHORN)

    # Wrizz check
    if not touch_img_wait("buttons/quickbattle"):
        logger.warning("Wrizz quick battle not found")
    else:
        logger.info("Wrizz found, collecting...")
        touch_xy_wait(725, 1300)
        # So we don't get stuck on capped resources screen
        touch_img_wait("buttons/confirm")
        touch_xy_wait(550, 500)
        touch_xy_wait(550, 500, seconds=2)

    # Soren Check
    touch_xy_wait(970, 890)
    if not touch_img_wait("buttons/quickbattle"):
        logger.warning("Soren quick battle not found")
    else:
        logger.info("Soren found, collecting...")
        touch_xy_wait(725, 1300)
        # So we don't get stuck on capped resources screen
        touch_img_wait("buttons/confirm")
        touch_xy_wait(550, 500)
        touch_xy_wait(550, 500, seconds=2)

    logger.info("Guild hunts battled")

    touch_xy_wait(70, 1810)
    touch_xy_wait(70, 1810)


# Checks for completed quests and collects, then touch_img_waits the open chect and clears rewards
# Once for Dailies once for Weeklies
def collect_quests() -> None:
    logger.info("Collecting quests...")
    reset_to_screen()

    if not touch_img_when_visible("menus/quests"):
        logger.error("Quests not found")
        reset_to_screen()
        return

    if wait_until_img_visible("buttons/collect_quest", timeout_s=3):
        logger.debug("Collecting daily quests...")
        touch_img("buttons/collect_quest")
        touch_img_when_visible("buttons/fullquestchest", timeout_s=3)
        wait(0.25)
        touch_escape()
    touch_xy_wait(600, 1650)  # Weeklies
    if wait_until_img_visible("buttons/collect_quest", timeout_s=3):
        logger.debug("Collecting weekly quests...")
        touch_img("buttons/collect_quest")
        touch_img_when_visible("buttons/fullquestchest", timeout_s=3)
        wait(0.25)
        touch_escape_wait()
        # Second in case we get Limited Rewards popup
        if not locate_img("buttons/back"):
            touch_escape()
    logger.info("Quests collected")

    touch_img_when_visible("buttons/back")


def collect_merchants() -> None:
    logger.info("Collecting merchant deals...")

    touch_xy_wait(120, 300, seconds=5)

    if touch_img_wait("buttons/funinthewild", seconds=2):
        touch_xy_wait(250, 1820, seconds=2)  # Ticket
        touch_xy_wait(250, 1820, seconds=2)  # Reward

    drag_wait((1000, 1825), (100, 1825), 500)

    if not locate_img("buttons/noblesociety"):
        logger.error("Nobles not found")
        reset_to_screen()
        return

    logger.info("Collecting nobles...")
    touch_xy_wait(675, 1825)
    if locate_img("buttons/confirm_nobles", confidence=0.8, retry=2):
        logger.warning("Noble resource collection screen not found, skipping")
        touch_xy_wait(70, 1810)
    else:
        # Regal
        touch_xy_wait(750, 1600)  # Icon
        touch_xy_wait(440, 1470, seconds=0.5)
        touch_xy_wait(440, 1290, seconds=0.5)
        touch_xy_wait(440, 1100, seconds=0.5)
        touch_xy_wait(440, 915, seconds=0.5)
        touch_xy_wait(440, 725, seconds=0.5)
        touch_xy_wait(750, 1600)  # Icon
        # Twisted
        touch_xy_wait(600, 1600)  # Icon
        touch_xy_wait(440, 1470, seconds=0.5)
        touch_xy_wait(440, 1290, seconds=0.5)
        touch_xy_wait(440, 1100, seconds=0.5)
        touch_xy_wait(440, 915, seconds=0.5)
        touch_xy_wait(440, 725, seconds=0.5)
        touch_xy_wait(600, 1600)  # Icon
        # Champs
        touch_xy_wait(425, 1600)  # Icon
        touch_xy_wait(440, 1470, seconds=0.5)
        touch_xy_wait(440, 1290, seconds=0.5)
        touch_xy_wait(440, 1100, seconds=0.5)
        touch_xy_wait(440, 915, seconds=0.5)
        touch_xy_wait(440, 725, seconds=0.5)
        touch_xy_wait(450, 1600)  # Icon
    # Monthly Cards
    logger.info("Collecting monthly cards...")
    touch_xy_wait(400, 1825)
    # Monthly
    touch_xy_wait(300, 1000, seconds=3)
    touch_xy_wait(560, 430)
    # Deluxe Monthly
    touch_xy_wait(850, 1000, seconds=3)
    touch_xy_wait(560, 430)
    # Daily Deals
    drag_wait((200, 1825), (450, 1825), 1000, seconds=2)
    touch_xy_wait(400, 1825)
    # Special Deal, no check as its active daily
    logger.info("Collecting special deals...")
    touch_img_wait("buttons/dailydeals")
    touch_xy_wait(150, 1625)
    touch_xy_wait(150, 1625)
    # Daily Deal
    if touch_img_wait("buttons/merchant_daily", confidence=0.8, retry=2):
        logger.info("Collecting daily deals...")
        drag_wait((550, 1400), (550, 1200), 500, seconds=3)
        touch_img_wait("buttons/dailydeals", confidence=0.8, retry=2)
        touch_xy_wait(400, 1675, seconds=2)

    d = datetime.now()
    # Biweeklies
    if d.isoweekday() == 3:  # Wednesday
        if touch_img_wait(
            "buttons/merchant_biweekly",
            confidence=0.8,
            retry=2,
        ):
            logger.info("Collecting bi-weekly deals...")
            drag_wait((300, 1400), (200, 1200), 500, seconds=3)
            touch_xy_wait(200, 1200)
            touch_xy_wait(550, 1625, seconds=2)
    # Yuexi
    if d.isoweekday() == 1:  # Monday
        logger.info("Collecting Yuexi...")
        touch_xy_wait(200, 1825)
        touch_xy_wait(240, 880)
        touch_xy_wait(150, 1625, seconds=2)
    # Clear Rhapsody bundles notification
    logger.info("Clearing rhapsody bundles notification...")
    drag_wait((200, 1825), (1000, 1825), 450, seconds=2)
    if touch_img_wait("labels/wishing_ship", confidence=0.8, retry=2):
        touch_xy_wait(620, 1600)
        touch_xy_wait(980, 200)
        touch_xy_wait(70, 1810)
        touch_xy_wait(70, 1810)

    logger.info("Merchant deals collected")

    reset_to_screen()


# Opens Twisted Realm and runs it once with whatever formation is loaded
def battle_tr() -> None:
    logger.info("Battling Twisted Realm...")
    reset_to_screen(Screen.RANHORN)

    touch_xy_wait(380, 360, seconds=6)
    touch_xy_wait(550, 1800)  # Clear chests
    touch_xy_wait(775, 875, seconds=2)
    touch_xy_wait(550, 600, seconds=3)

    if not locate_img("buttons/nextboss"):
        logger.error("Error opening Twisted Realm")
        # TODO Add 'Calculating' confirmation to exit safely
        reset_to_screen(Screen.RANHORN)
        return

    if not locate_img("buttons/challenge_tr", confidence=0.8, retry=3):
        logger.error("Challenge button not found, attempting to recover")
        touch_xy_wait(70, 1800)
        touch_xy_wait(70, 1800)
        reset_to_screen(Screen.RANHORN)
        return

    touch_xy_wait(550, 1850, seconds=2)
    touch_img_wait("buttons/autobattle", seconds=2, retry=3)
    if locate_img("buttons/checkbox_blank"):
        touch_xy_wait(300, 975)  # Activate Skip Battle Animations
    touch_xy_wait(700, 1300, seconds=6)
    touch_xy_wait(550, 1300)
    touch_xy_wait(550, 1800)
    touch_xy_wait(70, 1800)
    touch_xy_wait(70, 1800)
    # wait before next task as loading ranhorn can be slow
    touch_xy_wait(70, 1800, seconds=4)
    logger.info("Twisted Realm attempted successfully")

    reset_to_screen(Screen.RANHORN)


# Opens a Fight of Fates battle and then cycles between drag_waitging heroes and drag_waitging skills until we see the battle end screen
# Collects quests at the end
def fight_of_fates(settings: ChallengeSettings) -> None:
    t = settings["battles"]
    logger.info(f"Battling Fight of Fates {t} times")
    expand_menus()

    touch_img_wait("buttons/fightoffates", confidence=0.8, retry=5, seconds=3)

    if not locate_img("labels/fightoffates"):
        logger.warning("Fight of Fates not found")
        reset_to_screen()
        return

    for i in range(settings["battles"]):
        touch_img_wait("buttons/challenge_tr", confidence=0.8, seconds=15, retry=3)
        while not locate_img("labels/fightoffates", confidence=0.95):
            # Hero
            drag_wait((200, 1700), (290, 975), 200)
            # Skill 1
            drag_wait((450, 1700), (550, 950), 200)
            # Hero
            drag_wait((200, 1700), (290, 975), 200)
            # Skill 2
            drag_wait((600, 1700), (550, 950), 200)
            # Hero
            drag_wait((200, 1700), (290, 975), 200)
            # Skill 3
            drag_wait((800, 1700), (550, 950), 200)

        logger.info(f"Fight of Fates Battle #{i} complete")

    # Click quests
    touch_xy_wait(975, 125, seconds=2)
    # select dailies tab
    touch_xy_wait(650, 1650, seconds=1)
    # Collect Dailies
    touch_xy_wait(940, 680, seconds=2)
    touch_xy_wait(980, 435, seconds=2)
    # clear loot
    touch_xy_wait(550, 250, seconds=2)
    logger.info("Fight of Fates battled")

    # Back twice to exit
    touch_xy_wait(70, 1650, seconds=1)
    touch_xy_wait(70, 1810, seconds=1)


# Basic support for dailies quests, we simply choose the 5 cards from the top row of our hand
# Ater starting a battle we read the Stage 1/2/3 text at the top to determine when our opponent has placed their cards and to continue with placing ours
# Timeout is probably 10 seconds longer than the stage timer so if we exceed that something has gone wrong
# A round can take between 40 seconds or over 2 minutes depending on if our opponent is afk or not, at the end we collect daily quests
def battle_of_blood(settings: ChallengeSettings) -> None:
    t = settings["battles"]
    logger.info(f"Battling Battle of Blood {t} times...")
    expand_menus()

    touch_img_wait("buttons/events", confidence=0.8, seconds=3, retry=3)

    if not touch_img_wait("labels/battleofblood_event_banner"):
        logger.warning("Battle of Blood not found")
        reset_to_screen()
        return

    bob_timeout = 0  # Timer for tracking if something has gone wrong with placing cards
    for i in range(settings["battles"]):
        touch_img_wait("buttons/challenge_tr", confidence=0.8, seconds=7, retry=3)
        # Place cards 1-2, touch_img_wait ready
        while not locate_img("labels/battleofblood_stage1", (465, 20, 150, 55)):
            wait(1)
            bob_timeout += 1
            if bob_timeout > 30:
                logger.error("Battle of Blood timeout!")
                reset_to_screen()
                return
        else:
            wait(4)  # For the card animations
            bob_timeout = 0  # reset timer
            touch_xy_wait(550, 1250, seconds=1)
            touch_xy_wait(350, 1250, seconds=1)
            touch_xy_wait(550, 1850, seconds=1)
        if locate_img("buttons/confirm_small", (600, 1220, 200, 80), retry=3):
            touch_xy_wait(325, 1200)
            touch_xy_wait(700, 1270)
        # Place cards 3-4, touch_img_wait ready
        while not locate_img("labels/battleofblood_stage2", (465, 20, 150, 55)):
            wait(1)
            bob_timeout += 1
            if bob_timeout > 30:
                logger.error("Battle of Blood timeout!")
                reset_to_screen()
                return
        else:
            wait(4)  # For the card animations
            bob_timeout = 0  # reset timer
            touch_xy_wait(550, 1250, seconds=1)
            touch_xy_wait(350, 1250, seconds=1)
            touch_xy_wait(550, 1850, seconds=1)
        # Place card 5, touch_img_wait ready
        # higher confidence so we don't get confused with battleofblood_stage2.png
        while not locate_img("labels/battleofblood_stage3", (465, 20, 150, 55), 0.95):
            wait(1)
            bob_timeout += 1
            if bob_timeout > 30:
                logger.error("Battle of Blood timeout!")
                reset_to_screen()
                return
        else:
            wait(4)  # For the card animations
            bob_timeout = 0  # reset timer
            touch_xy_wait(550, 1250, seconds=1)
            touch_xy_wait(550, 1850, seconds=8)

            # Return Battle Report
            if get_battle_results("BoB"):
                logger.info(f"Victory! Battle of Blood Battle #{i + 1} complete")
            else:
                logger.warning(f"Defeat! Battle of Blood Battle #{i + 1} complete")

    # Click quests
    wait(2)  # wait for animations to settle from exting last battle
    touch_xy_wait(150, 230, seconds=2)
    # select dailies tab
    touch_xy_wait(650, 1720, seconds=1)
    # Collect Dailies
    touch_xy_wait(850, 720, seconds=3)
    touch_xy_wait(920, 525, seconds=2)
    touch_xy_wait(920, 525, seconds=2)
    # clear loot
    touch_xy_wait(550, 250, seconds=2)
    # Back twice to exit
    touch_xy_wait(70, 1810, seconds=1)  # Exit Quests
    touch_xy_wait(70, 1810, seconds=1)  # Exit BoB
    touch_xy_wait(70, 1810, seconds=1)  # Exit Events screen
    logger.info("Battle of Blood battled")

    reset_to_screen()


def circus_tour(settings: ChallengeSettings) -> None:
    logger.info("Battling Circus Tour...")
    reset_to_screen(Screen.RANHORN)

    expand_menus()  # Expand left menu again as it can shut after other dailies activities
    touch_img_wait("buttons/events", confidence=0.8, retry=3, seconds=3)
    if not touch_img_wait("labels/circustour", retry=3):
        logger.warning("Circus Tour not found, recovering..")
        reset_to_screen()
        return

    for i in range(settings["battles"]):
        touch_img_wait("buttons/challenge_tr", confidence=0.8, seconds=3, retry=3)

        if i == 1:
            # If Challenge is covered by text we clear it
            while locate_img("labels/dialogue_left", retry=2):
                logger.warning("Clearing dialogue..")
                touch_xy_wait(550, 900)  # Clear dialogue box on new boss rotation
                touch_xy_wait(550, 900)  # Only need to do this on the first battle
                touch_xy_wait(550, 900)
                touch_xy_wait(550, 900)
                touch_xy_wait(550, 900)
                touch_xy_wait(550, 900, seconds=2)
                touch_img_wait(
                    "buttons/challenge_tr", confidence=0.8, seconds=3, retry=3
                )

        touch_img_wait("buttons/battle_large", confidence=0.8, seconds=5, retry=3)
        touch_img_wait("buttons/skip", confidence=0.8, seconds=5, retry=5)
        touch_xy_wait(550, 1800)  # Clear loot

    wait(3)
    touch_xy_wait(500, 1600)  # First chest
    touch_xy_wait(500, 1600)  # Twice to clear loot popup
    touch_xy_wait(900, 1600)  # Second chest
    touch_xy_wait(900, 1600)  # Twice to clear loot popup

    logger.info("Circus Tour attempted successfully")

    # Back twice to exit
    touch_xy_wait(70, 1810, seconds=1)
    touch_xy_wait(70, 1810, seconds=1)
    reset_to_screen()


def run_lab() -> None:
    logger.info("Running Arcane Labyrinth...")
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy(400, 1150)
    wait_until_img_visible("labels/lab", timeout_s=3)

    if locate_img("labels/lablocked"):
        logger.info("Dismal Lab not unlocked")
        touch_xy(50, 1800)  # Exit Lab Menu
        return

    if locate_img("labels/labswept"):
        logger.info("Lab already swept")
        touch_xy(50, 1800)  # Exit Lab Menu
        return

    # Check for Sweep
    if touch_img("buttons/labsweep"):
        logger.info("Sweep available!")
        touch_img_when_visible("buttons/labsweepbattle")
        wait()
        touch_xy_wait(720, 1450, seconds=3)  # Click Confirm
        touch_xy_wait(550, 1550, seconds=3)  # Clear Rewards
        # And again for safe measure
        if locate_img("labels/notice", retry=3):
            touch_xy_wait(550, 1250)
        # Clear Roamer
        touch_img_when_visible("buttons/exitmenu")
        # Clear popup spam
        touch_img_when_visible("labels/tap-anywhere-to-close")
        logger.info("Lab swept!")
        return

    # Else we run lab manually
    logger.info("Sweep not found, running manually...")

    # Pre-run set up
    logger.info("Entering Lab")
    touch_xy_wait(750, 1100, seconds=2)  # Center of Dismal
    touch_xy_wait(550, 1475, seconds=2)  # Challenge
    touch_xy_wait(550, 1600, seconds=2)  # Begin Adventure
    touch_xy_wait(700, 1250, seconds=6)  # Confirm
    touch_xy_wait(550, 1600, seconds=3)  # Clear Debuff

    # TODO Check Dismal Floor 1 text
    logger.info("Sweeping all floors...")
    touch_xy_wait(950, 1600, seconds=2)  # Level Sweep
    touch_xy_wait(550, 1550, seconds=8)  # Confirm, long wait for animations
    touch_xy_wait(550, 1600, seconds=2)  # Clear Resources Exceeded message
    touch_xy_wait(550, 1600, seconds=2)  # And again for safe measure
    touch_xy_wait(550, 1600, seconds=3)  # Clear Loot
    touch_xy_wait(550, 1250, seconds=5)  # Abandon Roamer

    wait(6)  # Long pause for Value Bundle to pop up
    touch_xy_wait(550, 1650, seconds=3)  # Clear Value Bundle for completing lab
    touch_xy_wait(550, 550, seconds=3)  # Loot Chest
    touch_xy_wait(550, 1650, seconds=2)  # Clear Loot
    touch_xy_wait(550, 1650, seconds=2)  # Clear Notice
    touch_xy_wait(550, 1650, seconds=2)  # One more for safe measure
    touch_xy_wait(50, 1800, seconds=2)  # Click Back to Exit
    logger.info("Manual Lab run complete!")


# Returns result of a battle, diferent types for the different types of post-battle screens, count for number of battles in Arena
def get_battle_results(type) -> None:
    counter = 0

    if type == "BoB":
        while counter < 30:
            if locate_img("labels/victory"):
                touch_xy_wait(550, 1850, seconds=3)  # Clear window
                return True
            if locate_img("labels/defeat"):
                touch_xy_wait(550, 1850, seconds=3)  # Clear window
                return False
            counter += 1
        logger.error("Battletimer expired")
        reset_to_screen()
        return False

    # Here we don't clear the result by touch_img_waiting at the bottom as there is the battle report there
    if type == "HoE":
        while counter < 10:
            # Clear Rank Up message
            if locate_img(
                "labels/hoe_ranktrophy", retry=5, region=(150, 900, 350, 250)
            ):
                touch_xy_wait(550, 1200)
            if locate_img("labels/victory"):
                # logger.info('    Battle of Blood Victory!')
                touch_xy_wait(550, 700, seconds=3)  # Clear window
                return True
            if locate_img("labels/defeat"):
                # logger.error('    Battle of Blood Defeat!')
                touch_xy_wait(550, 700, seconds=3)  # Clear window
                return False
            counter += 1
        logger.error("Battletimer expired")
        return False

    if type == "arena":
        while counter < 10:
            if locate_img("labels/rewards"):
                return True
            if locate_img("labels/defeat"):
                return False
            wait(1)
            counter += 1
        logger.error("Arena battle timed out!")
        return False

    if type == "campaign":
        if locate_img("labels/victory", confidence=0.75, retry=2):
            logger.info("    Victory!")
            return True
        elif locate_img("labels/defeat", confidence=0.8):
            logger.error("    Defeat!")
            return False
        else:
            return "Unknown"


def challenge_hoe(settings: ChallengeOpponentSettings) -> None:
    t = settings["battles"]
    logger.info(f"Battling Heroes of Esperia {t} times...")
    logger.warning("Note: this currently won't work in the Legends Tower")
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy_wait(740, 1050)  # Open Arena of Heroes
    touch_xy_wait(550, 50)  # Clear Tickets Popup

    if not touch_img_wait("labels/heroesofesperia", seconds=3):
        logger.error("Heroes of Esperia not found")
        reset_to_screen(Screen.DARK_FOREST)
        return

    # Check if we've opened it yet
    if locate_img("buttons/join_hoe", (420, 1780, 250, 150), 0.8):
        logger.warning("Heroes of Esperia not opened! Entering..")
        touch_xy_wait(550, 1850)  # Clear Info
        touch_xy_wait(550, 1850, seconds=6)  # Click join
        touch_xy_wait(550, 1140, seconds=3)  # Clear Placement
        touch_xy_wait(1000, 1650, seconds=8)  # Collect all and wait for scroll
        touch_xy_wait(550, 260, seconds=5)  # Character portrait to clear Loot
        touch_xy_wait(550, 260, seconds=5)  # Character portrait to scroll back up

    # Start battles
    if not touch_img_wait(
        "buttons/fight_hoe", (400, 200, 400, 1500), seconds=3, retry=10
    ):
        logger.error("Heroes of Esperia Fight button not found! Recovering")
        reset_to_screen(Screen.DARK_FOREST)
        return

    for i in range(settings["battles"]):
        select_opponent(choice=settings["opponent_number"], hoe=True)
        # Check for ticket icon pixel
        if locate_img("labels/hoe_buytickets", (243, 618, 600, 120)):
            logger.error("Ticket Purchase screen found, exiting")
            reset_to_screen()
            return

        # This is rather than Battle button as that is animated and hard to read
        locate_img("buttons/heroclassselect", retry=3)
        touch_xy_wait(550, 1800)

        touch_img_when_visible("buttons/skip")
        if get_battle_results(type="HoE"):
            logger.info(f"Battle #{i + 1} victory!")
        else:
            logger.warning(f"Battle #{i + 1} defeat!")

        # Lots of things/animations can happen after a battle so we keep touch_img_waiting until we see the fight button again
        errorcounter = 0
        while not touch_img_wait("buttons/fight_hoe", (400, 200, 400, 1500), seconds=3):
            if errorcounter > 5:
                logger.error("Something went wrong post-battle")
                reset_to_screen(Screen.DARK_FOREST)
                return

            touch_escape_wait()
            touch_xy_wait(550, 1420)  # Rank up confirm button
            errorcounter += 1

    touch_img_wait("buttons/exitmenu")
    logger.info("Collecting Quests")
    touch_xy_wait(975, 300, seconds=2)  # Bounties
    touch_xy_wait(975, 220, seconds=2)  # Quests
    touch_xy_wait(850, 880, seconds=2)  # Top daily quest
    touch_xy_wait(550, 420, seconds=2)  # Click to clear loot
    touch_xy_wait(870, 1650, seconds=2)  # Season quests tab
    touch_xy_wait(850, 880, seconds=2)  # Top season quest
    touch_xy_wait(550, 420, seconds=2)  # Click to clear loot
    touch_img_wait("buttons/exitmenu", seconds=2)
    if check_pixel(550, 1850, 2) > 150:
        logger.info("Collecting Heroes of Esperia Pass loot")
        touch_xy_wait(550, 1800, seconds=2)  # Collect all at the pass screen
        touch_escape_wait()  # Click to clear loot
    logger.info("Heroes of Esperia battles complete")

    touch_img_when_visible_while_visible("buttons/back")
