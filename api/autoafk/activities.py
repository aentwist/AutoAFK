from datetime import datetime
from typing import Literal, TypedDict

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
    touch_escape_wait,
    touch_img,
    touch_img_wait,
    touch_img_when_visible,
    touch_img_when_visible_after_wait,
    touch_img_when_visible_while_visible,
    touch_img_while_other_visible,
    touch_xy_wait,
    wait,
    wait_until_img_visible,
)


boundaries = {
    # locate
    "campaignSelect": (424, 1750, 232, 170),
    "darkforestSelect": (208, 1750, 226, 170),
    "ranhornSelect": (0, 1750, 210, 160),
    # campaign/auto battle
    "begin": (322, 1590, 442, 144),
    "multiBegin": (309, 1408, 467, 129),
    "autobattle": (214, 1774, 256, 112),
    "battle": (574, 1779, 300, 110),
    "battleLarge": (310, 1758, 464, 144),
    "formations": (914, 1762, 102, 134),
    "useAB": (604, 1754, 242, 84),
    "confirmAB": (566, 1188, 252, 90),
    "activateAB": (580, 1208, 272, 86),
    "autobattle0": (562, 994, 144, 122),
    "autobattleLabel": (200, 578, 684, 178),
    "exitAB": (578, 1250, 290, 88),
    "cancelAB": (218, 1248, 298, 90),
    "pauseBattle": (24, 1419, 119, 104),
    "exitBattle": (168, 886, 130, 116),
    "tryagain": (478, 892, 128, 120),
    "continueBattle": (766, 888, 172, 128),
    "taptocontinue": (374, 1772, 330, 62),
    "kingstowerLabel": (253, 0, 602, 100),
    "challengeTower": (356, 726, 364, 1024),
    "heroclassselect": (5, 1620, 130, 120),
    "collectAfk": (590, 1322, 270, 82),
    "mailLocate": (874, 575, 190, 157),
    "collectMail": (626, 1518, 305, 102),
    "backMenu": (0, 1720, 150, 200),
    "friends": (880, 754, 178, 168),
    "sendrecieve": (750, 1560, 306, 100),
    "exitMerc": (912, 360, 129, 108),
    "fastrewards": (872, 1612, 130, 106),
    "closeFR": (266, 1218, 236, 92),
    "challengeAoH": (294, 1738, 486, 140),
    "attackAoH": (714, 654, 180, 606),
    "battleAoH": (294, 1760, 494, 148),
    "skipAoH": (650, 1350, 200, 200),
    "defeat": (116, 720, 832, 212),
    "exitAoH": (930, 318, 126, 132),
    # Misc
    "inngiftarea": (160, 1210, 500, 100),
    "dialogue_left": (40, 1550, 200, 300),
}


def collect_afk_rewards() -> None:
    logger.info("Collecting AFK rewards...")
    reset_to_screen()

    if not locate_img("buttons/campaign_selected", boundaries["campaignSelect"]):
        logger.error("AFK rewards button not found")
        return

    touch_xy_wait(550, 1550)
    touch_img_wait("buttons/collect", boundaries["collectAfk"], 0.8)
    touch_xy_wait(550, 1800)  # Click campaign in case we level up
    touch_xy_wait(550, 1800)  # again for the time limited deal popup
    logger.info("AFK rewards collected!")


# TODO: Check if mail. If not, we do not need to touch_escape.
def collect_mail() -> None:
    logger.info("Collecting mail...")
    reset_to_screen()

    if not (
        touch_img_when_visible("buttons/mail")
        and touch_img_when_visible("buttons/collect_all")
    ):
        logger.error("Mail not found")
    else:
        touch_escape()
        logger.info("Mail collected!")

    touch_img_when_visible_while_visible("buttons/back")


def send_and_receive_companion_points(mercs=False) -> None:
    logger.info("Sending/receiving companion points...")
    reset_to_screen()

    if not (
        touch_img_when_visible("buttons/friends")
        and touch_img_when_visible("buttons/sendandreceive")
    ):
        logger.error("No friends")
    else:
        logger.info("Companion points sent/received")

    if mercs:
        touch_xy_wait(720, 1760)  # Short term
        touch_xy_wait(990, 190)  # Manage
        touch_xy_wait(630, 1590)  # Apply
        touch_xy_wait(750, 1410)  # Auto lend
        touch_img_wait("buttons/exitmenu", region=boundaries["exitMerc"])
        logger.info("Mercenaries lent out")

    touch_img_when_visible_after_wait("buttons/back", seconds=0.25)


class CollectFastRewardsSettings(TypedDict):
    times: int


def collect_fast_rewards(settings: CollectFastRewardsSettings) -> None:
    t = settings["times"]
    logger.info(f"Collecting fast rewards {t} times...")
    reset_to_screen()

    if not locate_img("buttons/fastrewards", region=boundaries["fastrewards"]):
        logger.error("Fast rewards button not found")
        return

    # Check whether the pixel where the notification dot is has a high enough red value
    if not check_pixel(980, 1620, 0) > 220:
        logger.warning("Fast Rewards already done")
        return

    touch_xy_wait(950, 1660)
    for i in range(settings["times"]):
        touch_xy_wait(710, 1260, seconds=3)
        touch_xy_wait(550, 1800)
    logger.info("Fast rewards collected")

    touch_img_wait("buttons/close", region=boundaries["closeFR"])


# Loads and exits a campaign abttle for dailies quest
def attempt_campaign() -> None:
    logger.info("Attempting campaign battle...")
    reset_to_screen()

    touch_img_wait("buttons/begin", boundaries["begin"], seconds=2, retry=3)
    # Check if we're multi or single stage
    multi = locate_img("buttons/begin", boundaries["multiBegin"], 0.7, retry=3)
    logger.debug(f"{'Multi' if multi else 'Single'} stage detected")
    if multi:
        # Second button to enter multi
        touch_img_wait(
            "buttons/begin", boundaries["multiBegin"], 0.7, seconds=2, retry=5
        )

    # Many retries since on initial load this screen can take a while. Use
    # error handling due to the level of uncertainty.
    if not locate_img(
        "buttons/heroclassselect", retry=20, region=boundaries["heroclassselect"]
    ):
        logger.error("Hero class select button not found")
        reset_to_screen()
        return

    # Start and exit battle
    if multi:  # Multi has a different button for reasons
        touch_img_wait("buttons/beginbattle", boundaries["battle"], 0.7, seconds=4)
    else:
        touch_img_wait("buttons/battle", boundaries["battle"], 0.8, seconds=4)
    # Actions to exit an active fight and back out to the Campaign screen
    # 3 retries as ulting heroes can cover the button
    touch_img_wait("buttons/pause", boundaries["pauseBattle"], retry=3)
    touch_img_wait("buttons/exitbattle", boundaries["exitBattle"])
    touch_img_wait("buttons/back", boundaries["backMenu"], seconds=3, retry=3)
    logger.info("Campaign battle attempted")


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


# Handles the Bounty Board, calls dispatch_solo_bounties() to handle solo dust/diamond recognition and dispatching
def dispatch_bounties(settings: DispatchBountiesSettings) -> None:
    logger.info("Dispatching bounties...")
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy_wait(600, 1320)  # Open bounty board

    if not locate_img("labels/bountyboard", retry=3):
        logger.error("Bounty board not found")
        reset_to_screen(Screen.DARK_FOREST)
        return

    if settings["solo_bounties"]:
        touch_xy_wait(650, 1700)  # Solo tab
        touch_img_wait("buttons/collect_all", seconds=3)
        dispatch_solo_bounties(settings)

    if settings["team_bounties"]:
        touch_xy_wait(950, 1700)  # Team tab
        touch_img_wait("buttons/collect_all", seconds=2)
        touch_img_wait("buttons/dispatch", confidence=0.8, grayscale=True)
        touch_img_wait("buttons/confirm")

    # TODO::imgs-untested
    if settings["event_bounties"]:
        if touch_img_wait("labels/event_bounty"):
            touch_img_wait("buttons/collect_all", seconds=2)
            while touch_img_wait("buttons/dispatch_bounties"):
                touch_xy_wait(530, 1030, seconds=2)
                touch_xy_wait(120, 1500)
                touch_img_wait("buttons/dispatch", confidence=0.8, grayscale=True)

    logger.info("Bounties dispatched")

    touch_img_wait("buttons/back", boundaries["backMenu"])


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


# TODO::imgs-untested below


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
    touch_img_wait("buttons/challenge", boundaries["challengeAoH"], retry=3)

    for i in range(settings["battles"]):
        select_opponent(choice=settings["opponent_number"])
        # This is rather than Battle button as that is animated and hard to read
        while locate_img(
            "buttons/heroclassselect", boundaries["heroclassselect"], retry=3
        ):
            touch_xy_wait(550, 1800)
        # Retries as ulting heros can cover the button
        touch_img_wait("buttons/skip", boundaries["skipAoH"], 0.8, retry=5)
        if get_battle_results(type="arena"):
            logger.info(f"Battle #{i + 1} victory!")
            touch_xy_wait(600, 550)  # Clear loot popup
        else:
            logger.error(f"Battle #{i + 1} defeat!")
        touch_xy_wait(600, 550)  # Back to opponent selection

        handle_pause_and_stop_events()

    logger.info("Arena battles completed")

    touch_img_wait("buttons/exitmenu", region=boundaries["exitAoH"])
    touch_img_wait("buttons/back", retry=3, region=boundaries["backMenu"])
    touch_img_wait("buttons/back", retry=3, region=boundaries["backMenu"])


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

    touch_img_wait("buttons/back", region=boundaries["backMenu"])
    touch_img_wait("buttons/back", region=boundaries["backMenu"])


def use_bag_consumables() -> None:
    logger.info("Using bag consumables...")

    if not touch_img_when_visible("menus/bag"):
        logger.error("Bag not found, attempting to recover")
        reset_to_screen()
        return

    touch_img_wait("buttons/batchselect", retry=3)

    if locate_img("buttons/confirm_grey"):
        logger.warning("Nothing selected/available! Returning...")
        touch_img_wait("buttons/back", region=boundaries["backMenu"])
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
            touch_img_wait("buttons/back", region=boundaries["backMenu"])
            touch_img_wait("buttons/back", region=boundaries["backMenu"])
            return

    touch_xy_wait(550, 1800)  # Use
    touch_xy_wait(950, 1700)  # 'All' Bag button to clear loot
    logger.info("Bag consumables used")

    touch_img_wait("buttons/back", region=boundaries["backMenu"])


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
                touch_img_wait("buttons/back", boundaries["backMenu"], retry=3)
                touch_img_wait("buttons/back", boundaries["backMenu"], retry=3)
            else:
                touch_xy_wait(400, 50, seconds=2)  # Clear Rank Up
                touch_xy_wait(400, 50, seconds=2)  # Clear Loot
                touch_img_wait("buttons/back", retry=3, region=boundaries["backMenu"])
                touch_img_wait("buttons/back", retry=3, region=boundaries["backMenu"])
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


def open_tower(name) -> None:
    logger.info(f"Opening {name}...")
    reset_to_screen(Screen.DARK_FOREST)

    wait(3)  # Medium wait to make sure tower button is active
    touch_xy_wait(500, 870, seconds=3)  # Long pause for animation opening towers

    if not locate_img(
        "labels/kingstower", boundaries["kingstowerLabel"], 0.85, retry=3
    ):
        logger.error("Tower selection screen not found")
        reset_to_screen()
        return

    towers = {
        "King's Tower": [500, 870],
        "Lightbearer Tower": [300, 1000],
        "Wilder Tower": [800, 600],
        "Mauler Tower": [400, 1200],
        "Graveborn Tower": [800, 1200],
        "Hypogean Tower": [600, 1500],
        "Celestial Tower": [300, 500],
    }
    for tower, location in towers.items():
        if tower == name:
            touch_xy_wait(location[0], location[1], seconds=3)


class PushSettings(TypedDict):
    formation: int


# This is a long one, we have a whole host of fail safes because we want it to be as stable as possible
class TowerPusher:
    tower_open = False  # for defining if we need to open tower or not

    # Loads selected formation, enables auto-battle and periodically checks for victory
    def push_tower(tower, settings: PushSettings) -> None:
        # while True:
        # Open tower is needed then set it to enabled
        if TowerPusher.tower_open is False:
            open_tower(tower)
            TowerPusher.tower_open = True

        # Two checks, one for the Challenge button in the tower screen and one for the AutoBattle button on the hero selection screen
        # Both checks we check for two positives in a row so they aren't detected in the background while AutoBattle is running
        # If found we run config_battle_formation() to configure the formation and enable auto battle
        challengetimer = 0
        autobattletimer = 0
        # Challenge button
        while locate_img(
            "buttons/challenge_plain",
            boundaries["challengeTower"],
            0.8,
            seconds=2,
            retry=3,
        ):
            challengetimer += 1
            if challengetimer >= 2:
                touch_img_wait(
                    "buttons/challenge_plain",
                    boundaries["challengeTower"],
                    0.8,
                    seconds=3,
                    retry=3,
                )
                config_battle_formation(settings)
                challengetimer = 0
        # Autobattle button
        # higher confidence so we don't find it in the background
        while locate_img(
            "buttons/autobattle", boundaries["autobattle"], 0.92, seconds=2, retry=3
        ):
            autobattletimer += 1
            if autobattletimer >= 2:
                config_battle_formation(settings)
                autobattletimer = 0

        app_settings = app_settings_h.app_settings

        # We wait for the given duration (minus some time for configuring teams) then touch_xy_wait() to prompt the AutoBattle notice and check for victory
        wait((app_settings["victory_check_freq_min"] * 60) - 30)

        handle_pause_and_stop_events()

        touch_xy_wait(550, 1750)

        # Make sure the AutoBattle notice screen is visible
        # Make sure the popup is visible
        if locate_img("labels/autobattle", boundaries["autobattleLabel"], retry=2):
            # If it's 0 assume we haven't passed (not that bold an assumption..)
            if locate_img("labels/autobattle_0", boundaries["autobattle0"], retry=3):
                if not app_settings["surpress_victory_check_spam"]:
                    t = app_settings["victory_check_freq_min"]
                    logger.info(f"No victory found, checking again in {t} minutes.")

                touch_img_wait("buttons/cancel", boundaries["cancelAB"], retry=3)
            # If we don't see 0 we assume victory. We exit the battle, clear
            # victory screen and clear time limited rewards screen
            else:
                t = settings["formation"]
                logger.info(
                    f"Victory found! Loading the {t} formation for the current stage.."
                )

                touch_img_wait("buttons/exit", boundaries["exitAB"], retry=3)
                # 3 retries as ulting heroes can cover the button
                touch_img_wait("buttons/pause", boundaries["pauseBattle"], 0.8, retry=3)
                touch_img_wait("buttons/exitbattle", boundaries["exitBattle"], retry=2)
                touch_img_wait(
                    "labels/taptocontinue",
                    boundaries["taptocontinue"],
                    0.8,
                    seconds=4,
                    retry=2,
                    grayscale=True,
                )
                # To clear the Limited Rewards pop up every 20 stages
                touch_xy_wait(550, 1750)
        # If after touching we don't get the Auto Battle notice pop up, then
        # something has gone wrong so we reset and load push_tower again
        else:
            logger.warning("Autobattle screen not found, reloading auto-push...")
            reset_to_screen()
            TowerPusher.tower_open = False
            open_tower(tower)
            TowerPusher.tower_open = True


def push_campaign(settings: PushSettings) -> None:
    app_settings = app_settings_h.app_settings

    while True:
        if not touch_img_wait("buttons/begin", confidence=0.7, retry=3):
            if locate_img(
                "buttons/autobattle", boundaries["autobattle"], 0.95, seconds=2, retry=3
            ) and not locate_img("labels/autobattle"):
                config_battle_formation(settings)
            else:
                handle_pause_and_stop_events()
                touch_xy_wait(550, 1750)  # Click to prompt the AutoBattle popup

                if not locate_img("labels/autobattle"):
                    reset_to_screen()
                else:
                    # If it's 0 continue
                    if locate_img("labels/autobattle_0", boundaries["autobattle0"]):
                        if not app_settings["surpress_victory_check_spam"]:
                            t = app_settings["victory_check_freq_min"]
                            logger.warning(
                                f"No victory found, checking again in {t} minutes."
                            )
                        touch_img_wait(
                            "buttons/cancel", boundaries["cancelAB"], retry=3
                        )
                        wait((app_settings["victory_check_freq_min"] * 60) - 30)
                    else:  # If it's not 0 we have passed a stage
                        logger.info(
                            "Victory found! Loading the "
                            + str(
                                settings["formation"]
                                + " formation for the current stage.."
                            )
                        )
                        touch_img_wait("buttons/exit", boundaries["exitAB"], retry=3)
                        # 3 retries as ulting heroes can cover the button
                        touch_img_wait(
                            "buttons/pause", boundaries["pauseBattle"], 0.8, retry=3
                        )
                        touch_img_wait(
                            "buttons/exitbattle", boundaries["exitBattle"], retry=3
                        )
                        touch_img_wait(
                            "labels/taptocontinue",
                            boundaries["taptocontinue"],
                            0.8,
                            grayscale=True,
                        )


def config_battle_formation(settings: PushSettings) -> None:
    app_settings = app_settings_h.app_settings

    if app_settings["ignore_formations"]:
        logger.warning("ignoreformations enabled, skipping formation selection")
        touch_img_wait(
            "buttons/autobattle",
            suppress=True,
            retry=3,
            region=boundaries["autobattle"],
        )  # So we don't hit it in the background while autobattle is active
        touch_img_while_other_visible(
            "buttons/activate",
            "labels/autobattle",
            region=boundaries["activateAB"],
            secureregion=boundaries["autobattleLabel"],
        )
        return
    elif touch_img_wait(
        "buttons/formations", boundaries["formations"], seconds=3, retry=3
    ):
        if app_settings["use_popular_formations"]:  # Use popular formations tab
            touch_xy_wait(800, 1650, seconds=2)  # Change to 'Popular' tab
        touch_xy_wait(850, 425 + (settings["formation"] * 175), seconds=2)
        touch_img_wait("buttons/use", boundaries["useAB"], seconds=2, retry=3)

        # Configure Artifacts
        # loop because sometimes isVisible returns None here
        counter = 0
        artifacts = None
        while artifacts is None and counter <= 5:
            # Check checkbox status
            artifacts = locate_img("buttons/checkbox_checked", (230, 1100, 80, 80))
            counter += 1
        # If still None after 5 tries give error and contiue without configuring
        if counter >= 5:
            logger.error("Couldn't read artifact status")

        if artifacts is not app_settings["copy_artifacts"] and artifacts is not None:
            if app_settings["copy_artifacts"]:
                logger.info("Enabling Artifact copying")
            else:
                logger.info("Disabling Artifact copying")
            touch_xy_wait(275, 1150)

        touch_img_wait("buttons/confirm_small", boundaries["confirmAB"], retry=3)
        # So we don't hit it in the background while autobattle is active
        touch_img_wait("buttons/autobattle", boundaries["autobattle"], retry=3)
        touch_img_while_other_visible(
            "buttons/activate",
            "labels/autobattle",
            boundaries["activateAB"],
            boundaries["autobattleLabel"],
        )
    else:
        logger.warning("Could not find Formations button")


def attempt_kt() -> None:
    logger.info("Attempting Kings Tower battle...")
    reset_to_screen(Screen.DARK_FOREST)

    touch_xy_wait(500, 870, seconds=3)  # Long pause for animation

    if not locate_img("labels/kingstower"):
        logger.error("Tower screen not found")
        reset_to_screen(Screen.DARK_FOREST)
        return

    touch_xy_wait(555, 585)
    # lower confidence and retries for animated button
    touch_img_wait("buttons/challenge_plain", confidence=0.7, seconds=5, retry=5)
    # For reasons sometimes this button is 'beginbattle' and sometimes it is
    # 'begin', so we use touch_xy_wait
    touch_xy_wait(700, 1850, seconds=2)
    touch_img_wait("buttons/pause", confidence=0.8, retry=5)
    touch_img_wait("buttons/exitbattle")
    touch_img_when_visible_while_visible("buttons/back")
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
        if touch_img_wait(
            "buttons/inn_gift", boundaries["inngiftarea"], 0.75, seconds=2
        ):
            touch_xy_wait(550, 1400, seconds=0.5)  # Clear loot
            touch_xy_wait(550, 1400, seconds=0.5)  # Clear loot

    logger.info("Inn Gifts collected.")

    # wait before next task as loading ranhorn can be slow
    touch_img_wait("buttons/back", boundaries["backMenu"], seconds=2)


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
            while locate_img(
                "labels/dialogue_left", boundaries["dialogue_left"], retry=2
            ):
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

    touch_xy_wait(400, 1150, seconds=3)

    if locate_img("labels/labfloor3", confidence=0.8, retry=3):
        logger.info("Lab already open! Continuing..")
        touch_xy_wait(50, 1800, seconds=2)  # Exit Lab Menu
        return
    if locate_img("labels/lablocked", confidence=0.8):
        logger.info("Dismal Lab not unlocked! Continuing..")
        touch_xy_wait(50, 1800, seconds=2)  # Exit Lab Menu
        return

    # for whether we go left or right for the first battle
    lowerdirection = ""
    # For whether we go left or right to get the double battle at the end
    upperdirection = ""
    if locate_img("labels/lab", retry=3):
        # Check for Swept
        if locate_img("labels/labswept", confidence=0.8, retry=3):
            logger.info("Lab already swept! Continuing..")
            touch_xy_wait(50, 1800, seconds=2)  # Exit Lab Menu
            return
        # Check for Sweep
        if touch_img_wait("buttons/labsweep", confidence=0.8, seconds=3, retry=3):
            logger.info("Sweep available!")
            if touch_img_wait(
                "buttons/labsweepbattle", confidence=0.8, seconds=3, retry=3
            ):
                touch_xy_wait(720, 1450, seconds=3)  # Click Confirm
                touch_xy_wait(550, 1550, seconds=3)  # Clear Rewards
                # And again for safe measure
                if locate_img("labels/notice", retry=3):
                    touch_xy_wait(550, 1250)
                # Clear Roamer Deals, long wait for the Limited Offer to pop up for Lab completion
                touch_escape_wait(5)
                touch_escape()  # Clear Limited Offer
                logger.info("Lab swept!")
                return
        else:  # Else we run lab manually
            logger.info("Sweep not found, running manually...")

            # Pre-run set up
            logger.info("Entering Lab")
            touch_xy_wait(750, 1100, seconds=2)  # Center of Dismal
            touch_xy_wait(550, 1475, seconds=2)  # Challenge
            touch_xy_wait(550, 1600, seconds=2)  # Begin Adventure
            touch_xy_wait(700, 1250, seconds=6)  # Confirm
            touch_xy_wait(550, 1600, seconds=3)  # Clear Debuff
            # TODO Check Dismal Floor 1 text
            logger.info("Sweeping to 2nd Floor")
            touch_xy_wait(950, 1600, seconds=2)  # Level Sweep
            touch_xy_wait(550, 1550, seconds=8)  # Confirm, long wait for animations
            touch_xy_wait(550, 1600, seconds=2)  # Clear Resources Exceeded message
            touch_xy_wait(550, 1600, seconds=2)  # And again for safe measure
            touch_xy_wait(550, 1600, seconds=3)  # Clear Loot
            touch_xy_wait(550, 1250, seconds=5)  # Abandon Roamer
            logger.info("Choosing relics")
            for _ in range(6):
                touch_xy_wait(550, 900)  # Relic i
                touch_xy_wait(550, 1325, seconds=3)  # Choose
            logger.info("Entering 3rd Floor")
            touch_xy_wait(550, 550, seconds=2)  # Portal to 3rd Floor
            touch_xy_wait(550, 1200, seconds=5)  # Enter
            touch_xy_wait(550, 1600, seconds=2)  # Clear Debuff
            # TODO Check Dismal Floor 3 text

            # Check which route we are taking, as to avoid the cart
            touch_xy_wait(400, 1400, seconds=2)  # Open first tile on the left
            if locate_img("labels/labguard", retry=2):
                logger.warning("Loot Route: Left")
                lowerdirection = "left"
            else:
                logger.warning("Loot Route: Right")
                lowerdirection = "right"
                touch_xy_wait(550, 50, seconds=3)  # Back to Lab screen

            # 1st Row (single)
            handle_lab_tile(1, lowerdirection)
            # Check we're at the battle screen
            if locate_img("buttons/heroclassselect", retry=3):
                config_lab_teams(1)
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") == False:
                return

            # 2nd Row (multi)
            handle_lab_tile(2, lowerdirection)
            # Check we're at the battle screen
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab", firstOfMulti=True) is False:
                return
            touch_xy_wait(750, 1725, seconds=4)  # Continue to second battle
            # Check we're at the battle screen
            if locate_img("buttons/heroclassselect", retry=3):
                config_lab_teams(2)
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") is False:
                return

            # 3rd Row (single relic)
            handle_lab_tile(3, lowerdirection)
            # Check we're at the battle screen
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") is False:
                return
            touch_xy_wait(550, 1350, seconds=2)  # Clear Relic reward

            # 4th Row (multi)
            handle_lab_tile(4, lowerdirection)
            # Check we're at the battle screen
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab", firstOfMulti=True) is False:
                return
            touch_xy_wait(750, 1725, seconds=4)  # Continue to second battle
            # Check we're at the battle screen
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") is False:
                return

            # 5th Row (single)
            handle_lab_tile(5, lowerdirection)
            # Check we're at the battle screen
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") is False:
                return

            # 6th Row (single relic)
            handle_lab_tile(6, lowerdirection)
            # Check we're at the battle screen
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") is False:
                return
            touch_xy_wait(550, 1350, seconds=2)  # Clear Relic reward

            # Check which route we are taking for the upper tiles
            drag_wait((550, 200), (550, 1800), duration=1000)
            touch_xy_wait(400, 1450, seconds=2)  # First tile on the left
            if locate_img("labels/labpraeguard", retry=2):
                logger.warning("Loot Route: Left")
                upperdirection = "left"
            else:
                logger.warning("Loot Route: Right")
                upperdirection = "right"
                touch_xy_wait(550, 50, seconds=2)  # Back to Lab screen

            # 7th Row (multi)
            handle_lab_tile(7, upperdirection)
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab", firstOfMulti=True) is False:
                return
            touch_xy_wait(750, 1725, seconds=4)  # Continue to second battle
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") is False:
                return

            # 8th Row (multi)
            handle_lab_tile(8, upperdirection)
            if locate_img("buttons/heroclassselect", retry=3):
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab", firstOfMulti=True) is False:
                return
            touch_xy_wait(750, 1725, seconds=4)  # Continue to second battle
            if locate_img("buttons/heroclassselect", retry=3):
                # config_lab_teams(2, pet=False)  # We've lost heroes to Thoran etc by now, so lets re-pick 5 strongest heroes
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") is False:
                return

            # 9th Row (witches den or fountain)
            handle_lab_tile(9, upperdirection)
            if locate_img("labels/labwitchsden", retry=3):
                logger.warning("    Clearing Witch's Den")
                touch_xy_wait(550, 1500, seconds=3)  # Go
                touch_xy_wait(300, 1600, seconds=4)  # Abandon
            if locate_img("labels/labfountain", retry=3):
                logger.warning("    Clearing Divine Fountain")
                touch_xy_wait(725, 1250, seconds=3)  # Confirm
                touch_xy_wait(725, 1250, seconds=2)  # Go

            # 10th row (single boss)
            handle_lab_tile(10, upperdirection)
            if locate_img("buttons/heroclassselect", retry=3):
                config_lab_teams(
                    1, pet=False
                )  # We've lost heroes to Thoran etc by now, so lets re-pick 5 strongest heroes
                touch_xy_wait(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                reset_to_screen()
                return
            if get_battle_results(type="lab") is False:
                return

            wait(6)  # Long pause for Value Bundle to pop up
            touch_xy_wait(550, 1650, seconds=3)  # Clear Value Bundle for completing lab
            touch_xy_wait(550, 550, seconds=3)  # Loot Chest
            touch_xy_wait(550, 1650, seconds=2)  # Clear Loot
            touch_xy_wait(550, 1650, seconds=2)  # Clear Notice
            touch_xy_wait(550, 1650, seconds=2)  # One more for safe measure
            touch_xy_wait(50, 1800, seconds=2)  # Click Back to Exit
            logger.info("    Manual Lab run complete!")
    else:
        logger.error("Can't find Lab screen! Exiting..")
        reset_to_screen()


# Clears selected team and replaces it with top5 heroes, and 6th-10th for team2, selects pets from the first and second slots
def config_lab_teams(team: Literal[1, 2], pet=True) -> None:
    if team == 1:
        hero_y = 1300
        pet_x = 150
    else:
        hero_y = 1550
        pet_x = 350

    touch_xy_wait(1030, 1100, seconds=2)  # Clear Team
    touch_xy_wait(550, 1250, seconds=2)  # Confirm

    # Populate hero slots 5-1. Go in reverse order since top heroes tend to be
    # squishier so they get back line.
    for i in reversed(range(5)):
        touch_xy_wait(130 + i * 200, hero_y)  # Select
    # Choose pet
    if pet:
        if touch_img_wait("buttons/pet_empty", (5, 210, 140, 100), 0.75, retry=3):
            touch_xy_wait(pet_x, 1250, seconds=2)  # Select
            touch_xy_wait(750, 1800, seconds=4)  # Confirm


# Will select the correct Lab tile and take us to the battle screen
# Elevation is either Upper or Lower dependon on whether we have scrolled the screen up or not for the scond half
# Side is left or right, we choose once at the start and once after scrolling up to get both multi fights
# Tile is the row of the tile we're aiming for, from 1 at the bottom to 10 at the final boss
def handle_lab_tile(tile: int, side: Literal["right", "left"]) -> None:
    elevation = "upper" if tile > 6 else "lower"
    if tile in (4, 6, 10):
        logger.info(f"Battling {elevation} tile {tile}")
    else:
        logger.info(f"Battling {elevation} {side} tile {tile}")

    MULTI_TILES = (2, 4, 7, 8)
    RELIC_TILES = (3, 6)

    TILE_X_COEFF = (1, 2, 1, 0, 1, 0, 1, 2, 1, 0)
    tile_x_side_coeff = -1 if side == "left" else 1
    tile_x = 550 + tile_x_side_coeff * TILE_X_COEFF[tile - 1] * 150
    tile_y = 1450 - ((tile - 1) % 6) * 200

    touch_xy_wait(tile_x, tile_y, seconds=2)  # Tile
    # Not Witches Den or Well
    if tile != 9:
        # Not the 7th left, as there is no Go since we opened the tile to check
        # direction
        if not (tile == 7 and side == "left"):
            # Go slightly lower for relic tiles
            touch_xy_wait(550, 1600 if tile in RELIC_TILES else 1500, seconds=4)  # Go
        # Handle High Difficulty popup at first multi
        if tile == MULTI_TILES[0] and locate_img(
            "labels/notice", confidence=0.8, retry=3
        ):
            touch_xy_wait(450, 1150, seconds=2)  # Don't show this again
            touch_xy_wait(725, 1250, seconds=4)  # Go
        if tile in MULTI_TILES:
            touch_xy_wait(750, 1500, seconds=4)  # Begin Battle


# Returns result of a battle, diferent types for the different types of post-battle screens, count for number of battles in Arena
# firstOfMulti is so we don't touch_img_wait to clear loot after a lab battle, which would exit us from the battle screen for the second fight
def get_battle_results(type, firstOfMulti=False) -> None:
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

    if type == "lab":
        while counter < 15:
            # For 'resources exceeded' message
            if locate_img("labels/notice"):
                touch_xy_wait(550, 1250)
            if locate_img("labels/victory"):
                logger.info("    Lab Battle Victory!")
                if (
                    firstOfMulti is False
                ):  # Else we exit before second battle while trying to collect loot
                    touch_xy_wait(
                        550, 1850, seconds=5
                    )  # Clear loot popup and wait for Lab to load again
                return
            if locate_img("labels/defeat"):
                # TODO Use Duras Tears so we can continue
                logger.error("    Lab Battle  Defeat! Exiting..")
                reset_to_screen()
                return False
            counter += 1
        logger.error("Battletimer expired")
        reset_to_screen()
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
        locate_img("buttons/heroclassselect", boundaries["heroclassselect"], retry=3)
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

    touch_img_wait("buttons/exitmenu", region=boundaries["exitAoH"])
    logger.info("Collecting Quests")
    touch_xy_wait(975, 300, seconds=2)  # Bounties
    touch_xy_wait(975, 220, seconds=2)  # Quests
    touch_xy_wait(850, 880, seconds=2)  # Top daily quest
    touch_xy_wait(550, 420, seconds=2)  # Click to clear loot
    touch_xy_wait(870, 1650, seconds=2)  # Season quests tab
    touch_xy_wait(850, 880, seconds=2)  # Top season quest
    touch_xy_wait(550, 420, seconds=2)  # Click to clear loot
    touch_img_wait("buttons/exitmenu", region=boundaries["exitAoH"], seconds=2)
    if check_pixel(550, 1850, 2) > 150:
        logger.info("Collecting Heroes of Esperia Pass loot")
        touch_xy_wait(550, 1800, seconds=2)  # Collect all at the pass screen
        touch_escape_wait()  # Click to clear loot
    logger.info("Heroes of Esperia battles complete")

    touch_img_when_visible_while_visible("buttons/back")
