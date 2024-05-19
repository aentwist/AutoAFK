from math import ceil
from tools import *
import datetime
import shlex
import time
from typing import TypedDict

from logger import logger
from main import pauseOrStopEventCheck, settings


d = datetime.datetime.now()

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
    logger.info("Attempting AFK Reward collection")
    confirm_loc("campaign", region=boundaries["campaignSelect"])
    if is_visible("buttons/campaign_selected", region=boundaries["campaignSelect"]):
        click_xy(550, 1550)
        click("buttons/collect", 0.8, region=boundaries["collectAfk"])
        click_xy(550, 1800, seconds=1)  # Click campaign in case we level up
        click_xy(550, 1800, seconds=1)  # again for the time limited deal popup
        click_xy(550, 1800, seconds=1)  # 3rd to be safe
        logger.info("    AFK Rewards collected!")
    else:
        logger.error("AFK Rewards chests not found, recovering and will try again")
        recover()
        collect_afk_rewards()  # In case there was a popup to trial new hero


def collect_mail() -> None:
    logger.info("Attempting mail collection")
    if is_visible("buttons/mail", region=boundaries["mailLocate"]):
        wait()
        # if (check_pixel(1012, 610, 0) > 240): # We check if the pixel where the notification sits has a red value of higher than 240
        click_xy(960, 630, seconds=2)  # Click Mail
        click("buttons/collect_all", seconds=3, region=boundaries["collectMail"])
        click_xy(550, 1600)  # Clear any popups
        click("buttons/back", region=boundaries["backMenu"])
        logger.info("    Mail collected!")
        # else:
        #     logger.warning('    Mail notification not found')
    else:
        logger.error("Mail icon not found!")


def send_and_receive_companion_points(mercs=False) -> None:
    logger.info("Attempting to send/receive companion points")
    if is_visible("buttons/friends", region=boundaries["friends"]):
        if (
            check_pixel(1012, 790, 0) > 240
        ):  # We check if the pixel where the notification sits has a red value of higher than 240
            click_xy(960, 810)
            click("buttons/sendandreceive", region=boundaries["sendrecieve"])
            if mercs is True:
                click_xy(720, 1760)  # Short term
                click_xy(990, 190)  # Manage
                click_xy(630, 1590)  # Apply
                click_xy(750, 1410)  # Auto lend
                click("buttons/exitmenu", region=boundaries["exitMerc"])
                logger.info("    Mercenaries lent out")
            click("buttons/back", region=boundaries["backMenu"])
            logger.info("    Friends Points Sent")
        else:
            logger.warning("    Friends notification not found")


class CollectFastRewardsSettings(TypedDict):
    times: int


def collect_fast_rewards(settings: CollectFastRewardsSettings) -> None:
    logger.info(
        "Attempting to collecting Fast Rewards " + str(settings["times"]) + "x times"
    )
    counter = 0
    confirm_loc("campaign", region=boundaries["campaignSelect"])
    if is_visible("buttons/fastrewards", region=boundaries["fastrewards"]):
        if (
            check_pixel(980, 1620, 0) > 220
        ):  # We check if the pixel where the notification sits has a red value of higher than 240
            click_xy(950, 1660)
            while counter < settings["times"]:
                click_xy(710, 1260, seconds=3)
                click_xy(550, 1800)
                counter = counter + 1
            click("buttons/close", region=boundaries["closeFR"])
            logger.info("    Fast Rewards Done")
        else:
            logger.warning("    Fast Rewards already done")
    else:
        logger.error("    Fast Rewards icon not found!")


# Loads and exits a campaign abttle for dailies quest
def attempt_campaign() -> None:
    logger.info("Attempting Campaign battle")
    confirm_loc("campaign", region=boundaries["campaignSelect"])
    click("buttons/begin", seconds=2, retry=3, region=boundaries["begin"])
    # Check if we're multi or single stage
    multi = is_visible("buttons/begin", 0.7, retry=3, region=boundaries["multiBegin"])
    if multi:
        logger.info("    Multi stage detected")
        click(
            "buttons/begin", 0.7, retry=5, seconds=2, region=boundaries["multiBegin"]
        )  # Second button to enter multi
    else:
        logger.info("    Single stage detected")
    # Start and exit battle
    # Weird amount of retries as when loading the game for the first time this screen can take a while to load, so it acts as a counter
    if is_visible(
        "buttons/heroclassselect", retry=20, region=boundaries["heroclassselect"]
    ):  # Confirm we're on the hero selection screen
        if multi:  # Multi has different button for reasons
            click(
                "buttons/beginbattle",
                0.7,
                retry=3,
                seconds=3,
                region=boundaries["battle"],
            )
        else:
            click(
                "buttons/battle", 0.8, retry=3, seconds=3, region=boundaries["battle"]
            )
        # Actions to exit an active fight and back out to the Campaign screen
        click(
            "buttons/pause", retry=3, region=boundaries["pauseBattle"]
        )  # 3 retries as ulting heroes can cover the button
        click("buttons/exitbattle", retry=3, region=boundaries["exitBattle"])
        click(
            "buttons/back",
            retry=3,
            seconds=3,
            suppress=True,
            region=boundaries["backMenu"],
        )
        if confirm_loc("campaign", bool=True, region=boundaries["campaignSelect"]):
            logger.info("    Campaign attempted successfully")
    else:
        logger.error("    Something went wrong, attempting to recover")
        recover()


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
    logger.info("Handling Bounty Board")
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    click_xy(600, 1320)
    if is_visible("labels/bountyboard", retry=3):

        if settings["solo_bounties"]:
            click_xy(650, 1700)  # Solo tab
            is_visible("buttons/collect_all", seconds=3, click=True)
            dispatch_solo_bounties(settings)

        if settings["team_bounties"]:
            click_xy(950, 1700)  # Team tab
            click("buttons/collect_all", seconds=2, suppress=True)
            click("buttons/dispatch", confidence=0.8, suppress=True, grayscale=True)
            click("buttons/confirm", suppress=True)

        if settings["event_bounties"]:
            if is_visible("labels/event_bounty", click=True):
                click("buttons/collect_all", seconds=2, suppress=True)
                while is_visible("buttons/dispatch_bounties", click=True) == True:
                    click_xy(530, 1030, seconds=2)
                    click_xy(120, 1500)
                    click("buttons/dispatch", confidence=0.8, grayscale=True)

        click("buttons/back", region=boundaries["backMenu"])
        logger.info("    Bounties attempted successfully")
    else:
        logger.error("    Bounty Board not found, attempting to recover")
        recover()


# Loops through the bounty board returning found Dispatch buttons for dispatcher() to handle
# maxrefreshes is how many times to refresh before hitting dispatch all
# remaining is how many leftover bounties we should use dispatch all on rather than refresh again
def dispatch_solo_bounties(settings: DispatchSoloBountiesSettings) -> None:
    refreshes = 0
    while refreshes <= settings["max_refreshes"]:
        if refreshes > 0:
            logger.warning("    Board refreshed (#" + str(refreshes) + ")")
        dispatcher(
            get_dispatch_btns(), settings
        )  # Send the list to the function to dispatch
        swipe(550, 800, 550, 500, duration=200, seconds=2)  # scroll down
        dispatcher(
            get_dispatch_btns(scrolled=True), settings
        )  # Send the list to the function to dispatch
        if (
            refreshes >= 1
        ):  # quick read to see how many are left after the last dispatch, else we refresh the board needlessly before we do it
            if (
                len(get_dispatch_btns(scrolled=True))
                <= settings["number_remaining_to_dispatch_all"]
            ):  # if <=remaining bounties left we just dispatch all and continue
                logger.warning(
                    "  "
                    + str(settings["number_remaining_to_dispatch_all"])
                    + " or less bounties remaining, dispatching.."
                )
                click("buttons/dispatch", confidence=0.8, suppress=True, grayscale=True)
                click("buttons/confirm", suppress=True)
                return
        if refreshes < settings["max_refreshes"]:
            click_xy(90, 250)
            click_xy(700, 1250)
        refreshes += 1
    logger.info(
        "    "
        + str(settings["max_refreshes"])
        + " refreshes done, dispatching remaining.."
    )
    click("buttons/dispatch", confidence=0.8, suppress=True, grayscale=True)
    click("buttons/confirm", suppress=True)


# Recieves a list of Dispatch buttons Y coordinates and checks/dispatches the resource
def dispatcher(dispatches, settings: SoloBountySettings) -> None:
    # For loop over each button passed to the function
    for button in dispatches:
        # Names and Buttons
        bounty_types = {
            "dust": "labels/bounties/dust",
            "diamonds": "labels/bounties/diamonds",
            "juice": "labels/bounties/juice",
            "shards": "labels/bounties/shards",
            "gold": "labels/bounties/gold",
            "soulstone": "labels/bounties/soulstone",
        }
        # For each button we use `region=` to only check the resource in bounds to the left of it
        for resource, image in bounty_types.items():
            if is_visible(image, region=(30, button - 100, 140, 160), seconds=0):
                if (
                    resource != "gold" and resource != "soulstone"
                ):  # because there's no config setting for these
                    if settings[resource]:  # If it's enabled dispatch
                        logger.info("Dispatching " + resource.title())
                        click_xy(900, button)
                        click_xy(350, 1150)
                        click_xy(750, 1150)
                break  # Once resource is found and actions taken move onto the next button to save unnecessary checks


class ChallengeSettings(TypedDict):
    battles: int


class ChallengeOpponentSettings(ChallengeSettings):
    opponent_number: int


def challenge_arena(settings: ChallengeOpponentSettings, app) -> None:
    counter = 0
    logger.info("Battling Arena of Heroes " + str(settings["battles"]) + " times")
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    click_xy(740, 1050)
    click_xy(550, 50)
    if is_visible("labels/arenaofheroes_new"):  # The label font changes for reasons
        click("labels/arenaofheroes_new", suppress=True)
        click(
            "buttons/challenge", retry=3, region=boundaries["challengeAoH"]
        )  # retries for animated button
        while counter < settings["battles"]:
            wait(1)  # To avoid error when clickMultipleChoice returns no results
            select_opponent(choice=settings["opponent_number"])
            # clickMultipleChoice('buttons/arenafight', count=4, confidence=0.98, region=boundries['attackAoH'], seconds=3) # Select 4th opponent
            while is_visible(
                "buttons/heroclassselect", retry=3, region=boundaries["heroclassselect"]
            ):  # This is rather than Battle button as that is animated and hard to read
                click_xy(550, 1800)
            click(
                "buttons/skip",
                retry=5,
                confidence=0.8,
                suppress=True,
                region=boundaries["skipAoH"],
            )  # Retries as ulting heros can cover the button
            if get_battle_results(type="arena"):
                logger.info("    Battle #" + str(counter + 1) + " Victory!")
                click_xy(600, 550)  # Clear loot popup
            else:
                logger.error("    Battle #" + str(counter + 1) + " Defeat!")
            click_xy(600, 550)  # Back to opponent selection
            counter = counter + 1
            if pauseOrStopEventCheck(app.dailies_pause_event, app.dailies_stop_event):
                break  # Exit the loop if stop event is set
            if pauseOrStopEventCheck(app.activity_pause_event, app.activity_stop_event):
                break  # Exit the loop if stop event is set
        click("buttons/exitmenu", region=boundaries["exitAoH"])
        click("buttons/back", retry=3, region=boundaries["backMenu"])
        click("buttons/back", retry=3, region=boundaries["backMenu"])
        logger.info("    Arena battles complete")
    else:
        logger.error("Arena of Heroes not found, attempting to recover")
        recover()


def collect_gladiator_coins() -> None:
    logger.info("Collecting Gladiator Coins")
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    click_xy(740, 1050)
    click_xy(550, 50)
    swipe(550, 800, 550, 500, duration=200, seconds=2)  # scroll down
    if is_visible("labels/legendstournament_new"):  # The label font changes for reasons
        click("labels/legendstournament_new", suppress=True)
        click_xy(550, 300, seconds=2)
        click_xy(50, 1850)
        click("buttons/back", region=boundaries["backMenu"])
        click("buttons/back", region=boundaries["backMenu"])
        logger.info("    Gladiator Coins collected")
    else:
        logger.error("    Legends Tournament not found, attempting to recover")
        recover()


def use_bag_consumables() -> None:
    crashcounter = 0  # So we don't get stuck forever in the Use button loop
    logger.info("Using consumables from bag")
    click_xy(1000, 500, seconds=3)
    if is_visible("buttons/batchselect", click=True, retry=3):
        if is_visible("buttons/confirm_grey"):
            logger.warning("Nothing selected/available! Returning..")
            click("buttons/back", region=boundaries["backMenu"])
            return
        click_xy(550, 1650, seconds=2)
        while not is_visible("buttons/use_batch"):
            click_xy(
                550, 1800, seconds=0
            )  # 1 second check above is plenty so this is 0
            crashcounter += 1
            if crashcounter > 30:
                logger.error(
                    "Something went wrong (normally gear chests being selected), returning.."
                )
                click("buttons/back", region=boundaries["backMenu"])
                click("buttons/back", region=boundaries["backMenu"])
                return
        click_xy(550, 1800)  # Use
        click_xy(950, 1700)  # 'All' Bag button to clear loot
        click("buttons/back", region=boundaries["backMenu"], suppress=True)
        logger.info("    Bag consumables used!")
    else:
        logger.error("    Bag not found, attempting to recover")
        recover()


# TODO Get image for the fire debuff banner
def collect_ts_rewards() -> None:
    logger.info("Collecting Treasure Scramble daily loot")
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    click_xy(740, 1050)  # open Arena of Heroes
    click_xy(550, 50)  # Clear Arena Tickets
    ts_banners = [
        "labels/tsbanner_forest",
        "labels/tsbanner_ice",
        "labels/tsbanner_fog",
        "labels/tsbanner_volcano",
    ]
    for banner in ts_banners:  # Check the 4 debuffs
        if is_visible(banner, click=True):
            wait(2)
            if is_visible("buttons/ts_path", click=True):
                click_xy(370, 945)  # Choose path
                click_xy(520, 1700)  # Confirm path
                click("buttons/back", retry=3, region=boundaries["backMenu"])
                click("buttons/back", retry=3, region=boundaries["backMenu"])
                return
            else:
                click_xy(400, 50, seconds=2)  # Clear Rank Up
                click_xy(400, 50, seconds=2)  # Clear Loot
                click("buttons/back", retry=3, region=boundaries["backMenu"])
                click("buttons/back", retry=3, region=boundaries["backMenu"])
                logger.info("    Treasure Scramble daily loot collected!")
            return
    else:
        logger.error("    Treasure Scramble not found, attempting to recover")
        recover()


def collect_fountain_of_time() -> None:
    logger.info("Collecting Fountain of Time")
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    click_xy(800, 700, seconds=6)
    click_xy(800, 700, seconds=1)
    if is_visible("labels/temporalrift"):
        click_xy(550, 1800)
        click_xy(250, 1300)
        click_xy(700, 1350)  # Collect
        click_xy(550, 1800, seconds=3)  # Clear level up
        click_xy(550, 1800, seconds=3)  # Clear limited deal
        click_xy(550, 1800, seconds=3)  # Clear newly unlocked
        click("buttons/back", region=boundaries["backMenu"])
        logger.info("    Fountain of Time collected")
    else:
        logger.error("    Temporal Rift not found, attempting to recover")
        recover()


def open_tower(name) -> None:
    logger.info("Opening " + name + ".")
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    wait(3)  # Medium wait to make sure tower button is active when we click
    click_xy(500, 870, seconds=3)  # Long pause for animation opening towers
    if is_visible(
        "labels/kingstower",
        region=boundaries["kingstowerLabel"],
        retry=3,
        confidence=0.85,
    ):
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
                click_xy(location[0], location[1], seconds=3)
    else:
        logger.error("Tower selection screen not found.")
        recover()


class AppSettings(TypedDict):
    emulator_path: str
    port: int
    debug_mode: bool
    start_delay_min: int
    wait_multiplier: int
    victory_check_freq_min: int
    surpress_victory_check_spam: bool
    ignore_formations: bool
    use_popular_formations: bool
    copy_artifacts: bool
    hibernate_when_finished: bool


class PushSettings(TypedDict):
    formation: int


# This is a long one, we have a whole host of fail safes because we want it to be as stable as possible
class TowerPusher:
    tower_open = False  # for defining if we need to open tower or not

    # Loads selected formation, enables auto-battle and periodically checks for victory
    def push_tower(
        tower, settings: PushSettings, app_settings: AppSettings, app=None
    ) -> None:
        while app.push_thread_running:
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
            while is_visible(
                "buttons/challenge_plain",
                confidence=0.8,
                retry=3,
                seconds=2,
                region=boundaries["challengeTower"],
            ):
                challengetimer += 1
                if challengetimer >= 2:
                    click(
                        "buttons/challenge_plain",
                        confidence=0.8,
                        retry=3,
                        seconds=3,
                        region=boundaries["challengeTower"],
                    )
                    config_battle_formation(settings, app_settings)
                    challengetimer = 0
            # Autobattle button
            while is_visible(
                "buttons/autobattle",
                0.92,
                retry=3,
                seconds=2,
                region=boundaries["autobattle"],
            ):  # higher confidence so we don't find it in the background
                autobattletimer += 1
                if autobattletimer >= 2:
                    config_battle_formation(settings, app_settings)
                    autobattletimer = 0

            # We wait for the given duration (minus some time for configuring teams) then click_xy() to prompt the AutoBattle notice and check for victory
            wait((app_settings["victory_check_freq_min"] * 60) - 30)

            if pauseOrStopEventCheck(app.push_pause_event, app.push_stop_event):
                TowerPusher.tower_open = False
                break

            click_xy(550, 1750)

            # Make sure the AutoBattle notice screen is visible
            if is_visible(
                "labels/autobattle", retry=2, region=boundaries["autobattleLabel"]
            ):  # Make sure the popup is visible
                # If it's 0 assume we haven't passed (not that bold an assumption..)
                if is_visible(
                    "labels/autobattle_0", retry=3, region=boundaries["autobattle0"]
                ):
                    if not app_settings["surpress_victory_check_spam"]:
                        logger.warning(
                            "No victory found, checking again in "
                            + str(app_settings["victory_check_freq_min"] + " minutes.")
                        )
                    click(
                        "buttons/cancel",
                        retry=3,
                        suppress=True,
                        region=boundaries["cancelAB"],
                    )
                else:  # If we don't see 0 we assume victory. We exit the battle, clear victory screen and clear time limited rewards screen
                    logger.info(
                        "Victory found! Loading the "
                        + str(
                            settings["formation"] + " formation for the current stage.."
                        )
                    )
                    click(
                        "buttons/exit",
                        retry=3,
                        suppress=True,
                        region=boundaries["exitAB"],
                    )
                    click(
                        "buttons/pause",
                        0.8,
                        retry=3,
                        suppress=True,
                        region=boundaries["pauseBattle"],
                    )  # 3 retries as ulting heroes can cover the button
                    click(
                        "buttons/exitbattle",
                        retry=2,
                        suppress=True,
                        region=boundaries["exitBattle"],
                    )
                    click(
                        "labels/taptocontinue",
                        retry=2,
                        confidence=0.8,
                        suppress=True,
                        grayscale=True,
                        region=boundaries["taptocontinue"],
                    )
                    wait(3)
                    click_xy(
                        550, 1750
                    )  # To clear the Limited Rewards pop up every 20 stages
            else:  # If after clicking we don't get the Auto Battle notice pop up something has gone wrong so we recover() and load push_tower() again
                logger.warning("AutoBattle screen not found, reloading auto-push..")
                if recover() is True:
                    TowerPusher.tower_open = False
                    open_tower(tower)
                    TowerPusher.tower_open = True


def push_campaign(settings: PushSettings, app_settings: AppSettings, app) -> None:
    while app.push_thread_running:
        if is_visible("buttons/begin", 0.7, retry=3, click=True):
            continue

        if is_visible(
            "buttons/autobattle",
            0.95,
            retry=3,
            seconds=2,
            region=boundaries["autobattle"],
        ) and not is_visible("labels/autobattle"):
            config_battle_formation(settings, app_settings)
        else:
            if pauseOrStopEventCheck(app.push_pause_event, app.push_stop_event):
                break
            click_xy(550, 1750)  # Click to prompt the AutoBattle popup
            if is_visible("labels/autobattle"):
                if is_visible(
                    "labels/autobattle_0", region=boundaries["autobattle0"]
                ):  # If it's 0 continue
                    if not app_settings["surpress_victory_check_spam"]:
                        logger.warning(
                            "No victory found, checking again in "
                            + str(app_settings["victory_check_freq_min"] + " minutes.")
                        )
                    click(
                        "buttons/cancel",
                        retry=3,
                        suppress=True,
                        region=boundaries["cancelAB"],
                    )
                    wait(
                        (app_settings["victory_check_freq_min"] * 60) - 30
                    )  # Sleep for the wait duration
                else:  # If it's not 0 we have passed a stage
                    logger.info(
                        "Victory found! Loading the "
                        + str(
                            settings["formation"] + " formation for the current stage.."
                        )
                    )
                    click(
                        "buttons/exit",
                        suppress=True,
                        retry=3,
                        region=boundaries["exitAB"],
                    )
                    click(
                        "buttons/pause",
                        confidence=0.8,
                        retry=3,
                        suppress=True,
                        region=boundaries["pauseBattle"],
                    )  # 3 retries as ulting heroes can cover the button
                    click(
                        "buttons/exitbattle",
                        suppress=True,
                        retry=3,
                        region=boundaries["exitBattle"],
                    )
                    click(
                        "labels/taptocontinue",
                        confidence=0.8,
                        suppress=True,
                        grayscale=True,
                        region=boundaries["taptocontinue"],
                    )
            else:
                recover()


def config_battle_formation(settings: PushSettings, app_settings: AppSettings) -> None:
    artifacts = None
    counter = 0
    if app_settings["ignore_formations"]:
        logger.warning("ignoreformations enabled, skipping formation selection")
        click(
            "buttons/autobattle",
            suppress=True,
            retry=3,
            region=boundaries["autobattle"],
        )  # So we don't hit it in the background while autobattle is active
        secure_click(
            "buttons/activate",
            "labels/autobattle",
            region=boundaries["activateAB"],
            secureregion=boundaries["autobattleLabel"],
        )
        return
    elif is_visible("buttons/formations", region=boundaries["formations"]):
        click("buttons/formations", seconds=3, retry=3, region=boundaries["formations"])
        if app_settings["use_popular_formations"]:  # Use popular formations tab
            click_xy(800, 1650, seconds=2)  # Change to 'Popular' tab
        click_xy(850, 425 + (settings["formation"] * 175), seconds=2)
        click("buttons/use", retry=3, region=boundaries["useAB"], seconds=2)

        # Configure Artifacts
        while (
            artifacts is None and counter <= 5
        ):  # loop because sometimes isVisible returns None here
            artifacts = is_visible(
                "buttons/checkbox_checked", region=(230, 1100, 80, 80)
            )  # Check checkbox status
            counter += 1
        if (
            counter >= 5
        ):  # If still None after 5 tries give error and contiue without configuring
            logger.error("Couldn't read artifact status")
        if artifacts is not app_settings["copy_artifacts"] and artifacts is not None:
            if app_settings["copy_artifacts"]:
                logger.info("Enabling Artifact copying")
            else:
                logger.info("Disabling Artifact copying")
            click_xy(
                275, 1150
            )  # click_xy not ideal here but my brain is fried so it'll do for now

        click("buttons/confirm_small", retry=3, region=boundaries["confirmAB"])
        click(
            "buttons/autobattle", retry=3, region=boundaries["autobattle"]
        )  # So we don't hit it in the background while autobattle is active
        secure_click(
            "buttons/activate",
            "labels/autobattle",
            region=boundaries["activateAB"],
            secureregion=boundaries["autobattleLabel"],
        )
    else:
        logger.warning("Could not find Formations button")


def attempt_kt() -> None:
    logger.info("Attempting Kings Tower battle")
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    click_xy(500, 870, seconds=3)  # Long pause for animation
    if is_visible("labels/kingstower"):
        click_xy(555, 585)
        click(
            "buttons/challenge_plain", 0.7, retry=5, suppress=True, seconds=5
        )  # lower confidence and retries for animated button
        # For reasons sometimes this button is 'beginbattle' and sometimes it is 'begin', so we use click_xy
        click_xy(700, 1850, seconds=2)
        # click('buttons/beginbattle', 0.8, seconds=3, retry=5)
        click("buttons/pause", 0.8, retry=5, suppress=True)
        click("buttons/exitbattle")
        click("buttons/back", retry=3, region=boundaries["backMenu"])
        click("buttons/back", retry=3, region=boundaries["backMenu"])
        if is_visible("buttons/back", retry=3, region=boundaries["backMenu"]):
            click(
                "buttons/back", region=boundaries["backMenu"]
            )  # Last one only needed for multifights
        logger.info("    Tower attempted successfully")
    else:
        logger.error("Tower screen not found, attempting to recover")
        recover()


def collect_inn_gifts() -> None:
    checks = 0
    logger.info("Attempting daily Inn gift collection")
    confirm_loc("ranhorn", region=boundaries["ranhornSelect"])
    wait()
    click_xy(500, 200, seconds=4)
    if is_visible("buttons/manage"):
        while checks < 3:
            if is_visible(
                "buttons/inn_gift",
                confidence=0.75,
                click=True,
                region=boundaries["inngiftarea"],
                seconds=2,
            ):
                click_xy(550, 1400, seconds=0.5)  # Clear loot
                click_xy(550, 1400, seconds=0.5)  # Clear loot
                continue
            checks += 1
            wait()
        click("buttons/back", region=boundaries["backMenu"])
        logger.info("    Inn Gifts collected.")
        wait(2)  # wait before next task as loading ranhorn can be slow
    else:
        logger.error("    Inn not found, attempting to recover")
        recover()


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
            click_xy(pos[0], pos[1])
            click("buttons/shop/purchase", suppress=True)
            click_xy(550, 1220, seconds=2)

    # Scroll down so bottom row is visible
    swipe(550, 1500, 550, 1200, 500, seconds=5)

    # Purchase bottom 4 rows
    for item, button in bottomrow.items():
        if settings[item]:
            if is_visible(button, 0.95, click=True):
                logger.info("    Buying: " + item_name_map[item])
                click("buttons/shop/purchase", suppress=True)
                click_xy(550, 1220)
    wait(3)  # Long wait else Twisted Realm isn't found after if enabled in Dailies


def make_store_purchases(settings: MakeStorePurchasesSettings, skipQuick=0) -> None:
    if settings["quick_buy"] and skipQuick == 0:
        make_store_purchases_quick(settings["times"])
        return
    logger.info("Attempting store purchases " + str(settings["times"]) + " times")
    confirm_loc("ranhorn", region=boundaries["ranhornSelect"])
    wait(2)
    click_xy(300, 1725, seconds=5)
    if is_visible("labels/store"):
        # First purchases
        make_store_purchases_h(counter, settings)
        counter = 1
        # refresh purchases
        while counter < settings["times"]:
            click_xy(1000, 300)
            click("buttons/confirm", suppress=True, seconds=5)
            counter += 1
            logger.info("    Refreshed store " + str(counter) + " times.")
            make_store_purchases_h(counter, settings)
        click("buttons/back")
        logger.info("    Store purchases attempted.")
        wait(2)  # wait before next task as loading ranhorn can be slow
    else:
        logger.error("Store not found, attempting to recover")
        recover()


def make_store_purchases_quick(
    shoprefreshes, settings: MakeStorePurchasesSettings
) -> None:
    logger.info("Attempting store quickbuys (Refreshes: " + str(shoprefreshes) + ")")
    confirm_loc("ranhorn")
    wait(2)
    click_xy(300, 1725, seconds=5)
    if is_visible("labels/store"):
        if is_visible("buttons/quickbuy", click=True):
            wait(1)
            click("buttons/purchase", seconds=5)
            click_xy(970, 90, seconds=2)
            counter = 1
            while counter < shoprefreshes:
                click_xy(1000, 300)
                click("buttons/confirm", suppress=True, seconds=2)
                click("buttons/quickbuy", seconds=2)
                click("buttons/purchase", seconds=2)
                click_xy(970, 90)
                counter += 1
            click("buttons/back")
            logger.info("Store purchases attempted.")
        else:
            logger.info("Quickbuy not found, switching to old style")
            click("buttons/back")
            make_store_purchases(settings, 1)

    else:
        logger.error("Store not found, attempting to recover")
        recover()


def battle_guild_hunts() -> None:
    logger.info("Attempting to run Guild Hunts")
    confirm_loc("ranhorn", region=boundaries["ranhornSelect"])
    click_xy(380, 360)
    wait(6)
    click_xy(550, 1800)  # Clear chests
    # Collect any guild reward chests we have
    click("buttons/guild_chests", seconds=2)
    if is_visible("buttons/collect_guildchest"):
        click("buttons/collect_guildchest")
        click_xy(550, 1300)
        click_xy(900, 550)
        click_xy(550, 1800)  # Clear window
        wait(1)
    else:
        click_xy(550, 1800)  # Clear window
    click_xy(290, 860)
    # Wrizz check
    if is_visible("labels/wrizz"):
        if is_visible("buttons/quickbattle"):
            logger.info("    Wrizz Found, collecting")
            click("buttons/quickbattle")
            click_xy(725, 1300)
            # So we don't get stuck on capped resources screen
            if is_visible("buttons/confirm"):
                click("buttons/confirm")
            click_xy(550, 500)
            click_xy(550, 500, seconds=2)
        else:
            logger.warning("    Wrizz quick battle not found")
        # Soren Check
        click_xy(970, 890)
        if is_visible("buttons/quickbattle"):
            logger.info("    Soren Found, collecting")
            click("buttons/quickbattle")
            click_xy(725, 1300)
            # So we don't get stuck on capped resources screen
            if is_visible("buttons/confirm"):
                click("buttons/confirm")
            click_xy(550, 500)
            click_xy(550, 500, seconds=2)
        else:
            logger.warning("    Soren quick battle not found")
        click_xy(70, 1810)
        click_xy(70, 1810)
        logger.info("    Guild Hunts checked successfully")
    else:
        logger.error("    Error opening Guild Hunts, attempting to recover")
        recover()


# Checks for completed quests and collects, then clicks the open chect and clears rewards
# Once for Dailies once for Weeklies
def collect_quests() -> None:
    logger.info("Attempting to collect quest chests")
    click_xy(960, 250)
    if is_visible("labels/quests"):
        click_xy(400, 1650)  # Dailies
        if is_visible("labels/questcomplete"):
            logger.info("    Daily Quest(s) found, collecting..")
            click_xy(930, 680, seconds=4)  # Click top quest
            click("buttons/fullquestchest", seconds=3, retry=3, suppress=True)
            click_xy(400, 1650)
        click_xy(600, 1650)  # Weeklies
        if is_visible("labels/questcomplete"):
            logger.info("    Weekly Quest(s) found, collecting..")
            click_xy(930, 680, seconds=4)  # Click top quest
            click("buttons/fullquestchest", seconds=3, retry=3, suppress=True)
            click_xy(600, 1650, seconds=2)
            click_xy(600, 1650)  # Second in case we get Limited Rewards popup
        click("buttons/back", retry=3)
        logger.info("    Quests collected")
    else:
        logger.error("    Quests screen not found, attempting to recover")
        recover()


def collect_merchants() -> None:
    logger.info("Attempting to collect merchant deals")
    click_xy(120, 300, seconds=5)
    if is_visible("buttons/funinthewild", click=True, seconds=2):
        click_xy(250, 1820, seconds=2)  # Ticket
        click_xy(250, 1820, seconds=2)  # Reward
    swipe(1000, 1825, 100, 1825, 500)
    swipe(1000, 1825, 100, 1825, 500, seconds=3)
    if is_visible("buttons/noblesociety"):
        logger.info("    Collecting Nobles")
        # Nobles
        click_xy(675, 1825)
        if is_visible("buttons/confirm_nobles", 0.8, retry=2):
            logger.warning(
                "Noble resource collection screen found, skipping Noble collection"
            )
            click_xy(70, 1810)
        else:
            # Champion
            click_xy(750, 1600)  # Icon
            click_xy(440, 1470, seconds=0.5)
            click_xy(440, 1290, seconds=0.5)
            click_xy(440, 1100, seconds=0.5)
            click_xy(440, 915, seconds=0.5)
            click_xy(440, 725, seconds=0.5)
            click_xy(750, 1600)  # Icon
            # Twisted
            click_xy(600, 1600)  # Icon
            click_xy(440, 1470, seconds=0.5)
            click_xy(440, 1290, seconds=0.5)
            click_xy(440, 1100, seconds=0.5)
            click_xy(440, 915, seconds=0.5)
            click_xy(440, 725, seconds=0.5)
            click_xy(600, 1600)  # Icon
            # Regal
            click_xy(450, 1600)  # Icon
            click_xy(440, 1470, seconds=0.5)
            click_xy(440, 1290, seconds=0.5)
            click_xy(440, 1100, seconds=0.5)
            click_xy(440, 915, seconds=0.5)
            click_xy(440, 725, seconds=0.5)
            click_xy(450, 1600)  # Icon
        # Monthly Cards
        logger.info("    Collecting Monthly Cards")
        click_xy(400, 1825)
        # Monthly
        click_xy(300, 1000, seconds=3)
        click_xy(560, 430)
        # Deluxe Monthly
        click_xy(850, 1000, seconds=3)
        click_xy(560, 430)
        # Daily Deals
        swipe(200, 1825, 450, 1825, 1000, seconds=2)
        click_xy(400, 1825)
        # Special Deal, no check as its active daily
        logger.info("    Collecting Special Deal")
        click("buttons/dailydeals")
        click_xy(150, 1625)
        click_xy(150, 1625)
        # Daily Deal
        if is_visible("buttons/merchant_daily", confidence=0.8, retry=2, click=True):
            logger.info("    Collecting Daily Deal")
            swipe(550, 1400, 550, 1200, 500, seconds=3)
            click("buttons/dailydeals", confidence=0.8, retry=2)
            click_xy(400, 1675, seconds=2)
        # Biweeklies
        if d.isoweekday() == 3:  # Wednesday
            if is_visible(
                "buttons/merchant_biweekly", confidence=0.8, retry=2, click=True
            ):
                logger.info("    Collecting Bi-weekly Deal")
                swipe(300, 1400, 200, 1200, 500, seconds=3)
                click_xy(200, 1200)
                click_xy(550, 1625, seconds=2)
        # Yuexi
        if d.isoweekday() == 1:  # Monday
            logger.info("    Collecting Yuexi")
            click_xy(200, 1825)
            click_xy(240, 880)
            click_xy(150, 1625, seconds=2)
        # Clear Rhapsody bundles notification
        logger.info("    Clearing Rhapsody bundles notification")
        swipe(200, 1825, 1000, 1825, 450, seconds=2)
        if is_visible("labels/wishing_ship", confidence=0.8, retry=2, click=True):
            click_xy(620, 1600)
            click_xy(980, 200)
            click_xy(70, 1810)
            click_xy(70, 1810)
        logger.info("    Merchant deals collected")
        recover(True)
    else:
        logger.error("    Noble screen not found, attempting to recover")
        recover()


# Opens Twisted Realm and runs it once with whatever formation is loaded
def battle_tr() -> None:
    logger.info("Attempting to run Twisted Realm")
    confirm_loc("ranhorn", region=boundaries["ranhornSelect"])
    click_xy(380, 360, seconds=6)
    click_xy(550, 1800)  # Clear chests
    click_xy(775, 875, seconds=2)
    click_xy(550, 600, seconds=3)
    if is_visible("buttons/nextboss"):
        logger.info("    Twisted Realm found, battling")
        if is_visible("buttons/challenge_tr", retry=3, confidence=0.8):
            click_xy(550, 1850, seconds=2)
            click("buttons/autobattle", retry=3, seconds=2)
            if is_visible("buttons/checkbox_blank"):
                click_xy(300, 975)  # Activate Skip Battle Animations
            click_xy(700, 1300, seconds=6)
            click_xy(550, 1300)
            click_xy(550, 1800)
            click_xy(70, 1800)
            click_xy(70, 1800)
            click_xy(70, 1800)
            logger.info("    Twisted Realm attempted successfully")
            wait(3)  # wait before next task as loading ranhorn can be slow
            recover(True)
        else:
            click_xy(70, 1800)
            click_xy(70, 1800)
            logger.error("    Challenge button not found, attempting to recover")
            recover()
    else:
        logger.error("    Error opening Twisted Realm, attempting to recover")
        # TODO Add 'Calculating' confirmation to exit safely
        recover()


# Opens a Fight of Fates battle and then cycles between dragging heroes and dragging skills until we see the battle end screen
# Collects quests at the end
def fight_of_fates(settings: ChallengeSettings) -> None:
    logger.info(
        "Attempting to run Fight of Fates " + str(settings["battles"]) + " times"
    )
    counter = 0
    expand_menus()  # Expand left menu again as it can shut after other dailies activities
    click("buttons/fightoffates", confidence=0.8, retry=5, seconds=3)
    if is_visible("labels/fightoffates"):
        while counter < settings["battles"]:
            click(
                "buttons/challenge_tr",
                confidence=0.8,
                suppress=True,
                retry=3,
                seconds=15,
            )
            while not is_visible("labels/fightoffates", confidence=0.95):
                # Hero
                swipe(200, 1700, 290, 975, 200)
                # Skill 1
                swipe(450, 1700, 550, 950, 200)
                # Hero
                swipe(200, 1700, 290, 975, 200)
                # Skill 2
                swipe(600, 1700, 550, 950, 200)
                # Hero
                swipe(200, 1700, 290, 975, 200)
                # Skill 3
                swipe(800, 1700, 550, 950, 200)
            counter = counter + 1
            logger.info("    Fight of Fates Battle #" + str(counter) + " complete")
        # Click quests
        click_xy(975, 125, seconds=2)
        # select dailies tab
        click_xy(650, 1650, seconds=1)
        # Collect Dailies
        click_xy(940, 680, seconds=2)
        click_xy(980, 435, seconds=2)
        # clear loot
        click_xy(550, 250, seconds=2)
        # Back twice to exit
        click_xy(70, 1650, seconds=1)
        click_xy(70, 1810, seconds=1)
        logger.info("    Fight of Fates attempted successfully")
    else:
        logger.warning("Fight of Fates not found, recovering..")
        recover()


# Basic support for dailies quests, we simply choose the 5 cards from the top row of our hand
# Ater starting a battle we read the Stage 1/2/3 text at the top to determine when our opponent has placed their cards and to continue with placing ours
# Timeout is probably 10 seconds longer than the stage timer so if we exceed that something has gone wrong
# A round can take between 40 seconds or over 2 minutes depending on if our opponent is afk or not, at the end we collect daily quests
def battle_of_blood(settings: ChallengeSettings) -> None:
    logger.info(
        "Attempting to run Battle of Blood " + str(settings["battles"]) + " times"
    )
    battlecounter = 0  # Number of battles we want to run
    bob_timeout = 0  # Timer for tracking if something has gone wrong with placing cards
    expand_menus()  # Expand left menu again as it can shut after other dailies activities
    click("buttons/events", confidence=0.8, retry=3, seconds=3)
    if is_visible("labels/battleofblood_event_banner", click=True):
        while battlecounter < settings["battles"]:
            click(
                "buttons/challenge_tr",
                confidence=0.8,
                suppress=True,
                retry=3,
                seconds=7,
            )
            # Place cards 1-2, click ready
            while not is_visible(
                "labels/battleofblood_stage1", region=(465, 20, 150, 55)
            ):
                wait(1)
                bob_timeout += 1
                if bob_timeout > 30:
                    logger.error("Battle of Blood timeout!")
                    recover()
                    return
            else:
                wait(4)  # For the card animations
                bob_timeout = 0  # reset timer
                click_xy(550, 1250, seconds=1)
                click_xy(350, 1250, seconds=1)
                click_xy(550, 1850, seconds=1)
            if is_visible(
                "buttons/confirm_small", retry=3, region=(600, 1220, 200, 80)
            ):
                click_xy(325, 1200)
                click_xy(700, 1270)
            # Place cards 3-4, click ready
            while not is_visible(
                "labels/battleofblood_stage2", region=(465, 20, 150, 55)
            ):
                wait(1)
                bob_timeout += 1
                if bob_timeout > 30:
                    logger.error("Battle of Blood timeout!")
                    recover()
                    return
            else:
                wait(4)  # For the card animations
                bob_timeout = 0  # reset timer
                click_xy(550, 1250, seconds=1)
                click_xy(350, 1250, seconds=1)
                click_xy(550, 1850, seconds=1)
            # Place card 5, click ready
            while not is_visible(
                "labels/battleofblood_stage3",
                region=(465, 20, 150, 55),
                confidence=0.95,
            ):  # higher confidence so we don't get confused with battleofblood_stage2.png
                wait(1)
                bob_timeout += 1
                if bob_timeout > 30:
                    logger.error("Battle of Blood timeout!")
                    recover()
                    return
            else:
                wait(4)  # For the card animations
                bob_timeout = 0  # reset timer
                click_xy(550, 1250, seconds=1)
                click_xy(550, 1850, seconds=8)
                # Return Battle Report
                battlecounter += 1
                result = get_battle_results("BoB")
                if result is True:
                    logger.info(
                        "    Victory! Battle of Blood Battle #"
                        + str(battlecounter)
                        + " complete"
                    )
                else:
                    logger.error(
                        "    Defeat! Battle of Blood Battle #"
                        + str(battlecounter)
                        + " complete"
                    )
        # Click quests
        wait(2)  # wait for animations to settle from exting last battle
        click_xy(150, 230, seconds=2)
        # select dailies tab
        click_xy(650, 1720, seconds=1)
        # Collect Dailies
        click_xy(850, 720, seconds=3)
        click_xy(920, 525, seconds=2)
        click_xy(920, 525, seconds=2)
        # clear loot
        click_xy(550, 250, seconds=2)
        # Back twice to exit
        click_xy(70, 1810, seconds=1)  # Exit Quests
        click_xy(70, 1810, seconds=1)  # Exit BoB
        click_xy(70, 1810, seconds=1)  # Exit Events screen
        if confirm_loc("ranhorn", bool=True, region=boundaries["ranhornSelect"]):
            logger.info("    Battle of Blood attempted successfully")
        else:
            logger.warning("Issue exiting Battle of Blood, recovering..")
            recover()
    else:
        logger.warning("Battle of Blood not found, recovering..")
        recover()


def circus_tour(settings: ChallengeSettings) -> None:
    battlecounter = 1
    logger.info("Attempting to run Circus Tour battles")
    confirm_loc(
        "ranhorn", region=boundaries["ranhornSelect"]
    )  # Trying to fix 'buttons/events not found' error
    expand_menus()  # Expand left menu again as it can shut after other dailies activities
    click("buttons/events", confidence=0.8, retry=3, seconds=3)
    if is_visible("labels/circustour", retry=3, click=True):
        while battlecounter < settings["battles"]:
            logger.info("    Circus Tour battle #" + str(battlecounter))
            click(
                "buttons/challenge_tr",
                confidence=0.8,
                retry=3,
                suppress=True,
                seconds=3,
            )
            if battlecounter == 1:
                # If Challenge is covered by text we clear it
                while is_visible(
                    "labels/dialogue_left", retry=2, region=boundaries["dialogue_left"]
                ):
                    logger.warning("    Clearing dialogue..")
                    click_xy(550, 900)  # Clear dialogue box on new boss rotation
                    click_xy(550, 900)  # Only need to do this on the first battle
                    click_xy(550, 900)
                    click_xy(550, 900)
                    click_xy(550, 900)
                    click_xy(550, 900, seconds=2)
                    click(
                        "buttons/challenge_tr",
                        confidence=0.8,
                        retry=3,
                        suppress=True,
                        seconds=3,
                    )
            click(
                "buttons/battle_large",
                confidence=0.8,
                retry=3,
                suppress=True,
                seconds=5,
            )
            click("buttons/skip", confidence=0.8, retry=5, seconds=5)
            click_xy(550, 1800)  # Clear loot
            battlecounter += 1
        wait(3)
        click_xy(500, 1600)  # First chest
        click_xy(500, 1600)  # Twice to clear loot popup
        click_xy(900, 1600)  # Second chest
        click_xy(900, 1600)  # Twice to clear loot popup
        # Back twice to exit
        click_xy(70, 1810, seconds=1)
        click_xy(70, 1810, seconds=1)
        if confirm_loc("ranhorn", bool=True, region=boundaries["ranhornSelect"]):
            logger.info("    Circus Tour attempted successfully")
        else:
            logger.warning("Issue exiting Circus Tour, recovering..")
            recover()
    else:
        logger.warning("Circus Tour not found, recovering..")
        recover()


def run_lab() -> None:
    logger.info("Attempting to run Arcane Labyrinth")
    lowerdirection = ""  # for whether we go left or right for the first battle
    upperdirection = (
        ""  # For whether we go left or right to get the double battle at the end
    )
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    wait()
    click_xy(400, 1150, seconds=3)
    if is_visible("labels/labfloor3", retry=3, confidence=0.8, seconds=3):
        logger.info("Lab already open! Continuing..")
        click_xy(50, 1800, seconds=2)  # Exit Lab Menu
        return
    if is_visible("labels/lablocked", confidence=0.8, seconds=3):
        logger.info("Dismal Lab not unlocked! Continuing..")
        click_xy(50, 1800, seconds=2)  # Exit Lab Menu
        return
    if is_visible("labels/lab", retry=3):
        # Check for Swept
        if is_visible("labels/labswept", retry=3, confidence=0.8, seconds=3):
            logger.info("Lab already swept! Continuing..")
            click_xy(50, 1800, seconds=2)  # Exit Lab Menu
            return
        # Check for Sweep
        if is_visible(
            "buttons/labsweep", retry=3, confidence=0.8, click=True, seconds=3
        ):
            logger.info("    Sweep Available!")
            if is_visible(
                "buttons/labsweepbattle", retry=3, confidence=0.8, click=True, seconds=3
            ):
                click_xy(720, 1450, seconds=3)  # Click Confirm
                click_xy(550, 1550, seconds=3)  # Clear Rewards
                if is_visible(
                    "labels/notice", retry=3, seconds=3
                ):  # And again for safe measure
                    click_xy(550, 1250)
                click_xy(
                    550, 1550, seconds=5
                )  # Clear Roamer Deals, long wait for the Limited Offer to pop up for Lab completion
                click_xy(550, 1650)  # Clear Limited Offer
                logger.info("    Lab Swept!")
                return
        else:  # Else we run lab manually
            logger.info("    Sweep not found, attempting manual Lab run..")

            # Pre-run set up
            logger.info("    Entering Lab")
            click_xy(750, 1100, seconds=2)  # Center of Dismal
            click_xy(550, 1475, seconds=2)  # Challenge
            click_xy(550, 1600, seconds=2)  # Begin Adventure
            click_xy(700, 1250, seconds=6)  # Confirm
            click_xy(550, 1600, seconds=3)  # Clear Debuff
            # TODO Check Dismal Floor 1 text
            logger.info("    Sweeping to 2nd Floor")
            click_xy(950, 1600, seconds=2)  # Level Sweep
            click_xy(550, 1550, seconds=8)  # Confirm, long wait for animations
            click_xy(550, 1600, seconds=2)  # Clear Resources Exceeded message
            click_xy(550, 1600, seconds=2)  # And again for safe measure
            click_xy(550, 1600, seconds=3)  # Clear Loot
            click_xy(550, 1250, seconds=5)  # Abandon Roamer
            logger.info("    Choosing relics")
            click_xy(550, 900)  # Relic 1
            click_xy(550, 1325, seconds=3)  # Choose
            click_xy(550, 900)  # Relic 2
            click_xy(550, 1325, seconds=3)  # Choose
            click_xy(550, 900)  # Relic 3
            click_xy(550, 1325, seconds=3)  # Choose
            click_xy(550, 900)  # Relic 4
            click_xy(550, 1325, seconds=3)  # Choose
            click_xy(550, 900)  # Relic 5
            click_xy(550, 1325, seconds=3)  # Choose
            click_xy(550, 900)  # Relic 6
            click_xy(550, 1325, seconds=3)  # Choose
            logger.info("    Entering 3rd Floor")
            click_xy(550, 550, seconds=2)  # Portal to 3rd Floor
            click_xy(550, 1200, seconds=5)  # Enter
            click_xy(550, 1600, seconds=2)  # Clear Debuff
            # TODO Check Dismal Floor 3 text

            # Check which route we are taking, as to avoid the cart
            click_xy(400, 1400, seconds=2)  # Open first tile on the left
            if is_visible("labels/labguard", retry=2):
                logger.warning("    Loot Route: Left")
                lowerdirection = "left"
            else:
                logger.warning("    Loot Route: Right")
                lowerdirection = "right"
                click_xy(550, 50, seconds=3)  # Back to Lab screen

            # 1st Row (single)
            handle_lab_tile("lower", lowerdirection, "1")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                config_lab_teams(1)
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return

            # 2nd Row (multi)
            handle_lab_tile("lower", lowerdirection, "2")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab", firstOfMulti=True) is False:
                return
            click_xy(750, 1725, seconds=4)  # Continue to second battle
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                config_lab_teams(2)
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return

            # 3rd Row (single relic)
            handle_lab_tile("lower", lowerdirection, "3")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return
            click_xy(550, 1350, seconds=2)  # Clear Relic reward

            # 4th Row (multi)
            handle_lab_tile("lower", lowerdirection, "4")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab", firstOfMulti=True) is False:
                return
            click_xy(750, 1725, seconds=4)  # Continue to second battle
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return

            # 5th Row (single)
            handle_lab_tile("lower", lowerdirection, "5")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return

            # 6th Row (single relic)
            handle_lab_tile("lower", lowerdirection, "6")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return
            click_xy(550, 1350, seconds=2)  # Clear Relic reward

            # Check which route we are taking for the upper tiles
            swipe(550, 200, 550, 1800, duration=1000)
            click_xy(400, 1450, seconds=2)  # First tile on the left
            if is_visible("labels/labpraeguard", retry=2):
                logger.warning("    Loot Route: Left")
                upperdirection = "left"
            else:
                logger.warning("    Loot Route: Right")
                upperdirection = "right"
                click_xy(550, 50, seconds=2)  # Back to Lab screen

            # 7th Row (multi)
            handle_lab_tile("upper", upperdirection, "7")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab", firstOfMulti=True) is False:
                return
            click_xy(750, 1725, seconds=4)  # Continue to second battle
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return

            # 8th Row (multi)
            handle_lab_tile("upper", upperdirection, "8")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab", firstOfMulti=True) is False:
                return
            click_xy(750, 1725, seconds=4)  # Continue to second battle
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                # config_lab_teams(2, pet=False)  # We've lost heroes to Thoran etc by now, so lets re-pick 5 strongest heroes
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return

            # 9th Row (witches den or fountain)
            handle_lab_tile("upper", upperdirection, "9")
            if is_visible("labels/labwitchsden", retry=3):
                logger.warning("    Clearing Witch's Den")
                click_xy(550, 1500, seconds=3)  # Go
                click_xy(300, 1600, seconds=4)  # Abandon
            if is_visible("labels/labfountain", retry=3):
                logger.warning("    Clearing Divine Fountain")
                click_xy(725, 1250, seconds=3)  # Confirm
                click_xy(725, 1250, seconds=2)  # Go

            # 10th row (single boss)
            handle_lab_tile("upper", upperdirection, "10")
            if is_visible(
                "buttons/heroclassselect", retry=3
            ):  # Check we're at the battle screen
                config_lab_teams(
                    1, pet=False
                )  # We've lost heroes to Thoran etc by now, so lets re-pick 5 strongest heroes
                click_xy(550, 1850, seconds=4)  # Battle
            else:
                logger.error("Battle Screen not found! Exiting")
                recover()
                return
            if get_battle_results(type="lab") is False:
                return

            wait(6)  # Long pause for Value Bundle to pop up
            click_xy(550, 1650, seconds=3)  # Clear Value Bundle for completing lab
            click_xy(550, 550, seconds=3)  # Loot Chest
            click_xy(550, 1650, seconds=2)  # Clear Loot
            click_xy(550, 1650, seconds=2)  # Clear Notice
            click_xy(550, 1650, seconds=2)  # One more for safe measure
            click_xy(50, 1800, seconds=2)  # Click Back to Exit
            logger.info("    Manual Lab run complete!")
    else:
        logger.error("Can't find Lab screen! Exiting..")
        recover()


# Clears selected team and replaces it with top5 heroes, and 6th-10th for team2, selects pets from the first and second slots
def config_lab_teams(team, pet=True) -> None:
    if team == 1:
        click_xy(1030, 1100, seconds=2)  # Clear Team
        click_xy(550, 1250, seconds=2)  # Confirm
        click_xy(
            930, 1300
        )  # Slot 5 (Reverse order as our top heroes tend to be squishy so they get back line)
        click_xy(730, 1300)  # Slot 4
        click_xy(530, 1300)  # Slot 3
        click_xy(330, 1300)  # Slot 2
        click_xy(130, 1300)  # Slot 1
        if pet is True:
            if is_visible(
                "buttons/pet_empty",
                confidence=0.75,
                retry=3,
                click=True,
                region=(5, 210, 140, 100),
            ):
                click_xy(150, 1250, seconds=2)  # First Pet
                click_xy(750, 1800, seconds=4)  # Confirm
    if team == 2:
        click_xy(1030, 1100, seconds=2)  # Clear Team
        click_xy(550, 1250, seconds=2)  # Confirm
        click_xy(130, 1550)  # Slot 1
        click_xy(330, 1550)  # Slot 2
        click_xy(530, 1550)  # Slot 3
        click_xy(730, 1550)  # Slot 4
        click_xy(930, 1550)  # Slot 5
        if pet is True:
            if is_visible(
                "buttons/pet_empty",
                confidence=0.75,
                retry=3,
                click=True,
                region=(5, 210, 140, 100),
            ):
                click_xy(350, 1250, seconds=2)  # Second Pet
                click_xy(750, 1800, seconds=4)  # Confirm


# Will select the correct Lab tile and take us to the battle screen
# Elevation is either Upper or Lower dependon on whether we have scrolled the screen up or not for the scond half
# Side is left or right, we choose once at the start and once after scrolling up to get both multi fights
# Tile is the row of the tile we're aiming for, from 1 at the bottom to 10 at the final boss
def handle_lab_tile(elevation, side, tile) -> None:
    if tile == "4" or tile == "6" or tile == "10":
        logger.info("    Battling " + elevation.capitalize() + " Tile " + tile)
    else:
        logger.info(
            "    Battling "
            + elevation.capitalize()
            + " "
            + side.capitalize()
            + " Tile "
            + tile
        )
    wait(1)
    if elevation == "lower":
        if side == "left":
            if tile == "1":  # Single
                click_xy(400, 1450, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go
            if tile == "2":  # Multi
                click_xy(250, 1250, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Click Go
                if is_visible(
                    "labels/notice", confidence=0.8, retry=3
                ):  # 'High Difficulty popup at first multi'
                    click_xy(450, 1150, seconds=2)  # Don't show this again
                    click_xy(725, 1250, seconds=4)  # Go
                click_xy(750, 1500, seconds=4)  # Click Begin Battle
            if tile == "3":  # Single
                click_xy(400, 1050, seconds=2)  # Tile
                click_xy(550, 1600, seconds=4)  # Go (lower for relic)
            if tile == "4":  # Multi
                click_xy(550, 850, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Click Go
                click_xy(750, 1500, seconds=4)  # Click Begin Battle
            if tile == "5":  # Single
                click_xy(400, 650, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go
            if tile == "6":  # Single
                click_xy(550, 450, seconds=2)  # Tile
                click_xy(550, 1600, seconds=4)  # Go (lower for relic)
        if side == "right":
            if tile == "1":  # Single
                click_xy(700, 1450, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go
            if tile == "2":  # Multi
                click_xy(800, 1225, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Click Go
                if is_visible(
                    "labels/notice", confidence=0.8, retry=3
                ):  # 'High Difficulty popup at first multi'
                    click_xy(450, 1150, seconds=2)  # Don't show this again
                    click_xy(725, 1250, seconds=4)  # Go
                click_xy(750, 1500, seconds=4)  # Click Begin Battle
            if tile == "3":  # Single
                click_xy(700, 1050, seconds=2)  # Tile
                click_xy(550, 1600, seconds=4)  # Go (lower for relic)
            if tile == "4":  # Multi
                click_xy(550, 850, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Click Go
                click_xy(750, 1500, seconds=4)  # Click Begin Battle
            if tile == "5":  # Single
                click_xy(700, 650, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go
            if tile == "6":
                click_xy(550, 450, seconds=2)  # Tile
                click_xy(550, 1600, seconds=4)  # Go (lower for relic)
    if elevation == "upper":
        if side == "left":
            if tile == "7":  # Multi
                click_xy(400, 1450, seconds=2)  # Tile
                # No Go as we opened the tile to check direction
                click_xy(750, 1500, seconds=4)  # Click Begin Battle
            if tile == "8":  # Multi
                click_xy(250, 1250, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go
                click_xy(750, 1500, seconds=4)  # Click Begin Battle
            if tile == "9":  # Witches Den or Well
                click_xy(400, 1100, seconds=2)  # Tile
            if tile == "10":  # Single
                click_xy(550, 900, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go
        if side == "right":
            if tile == "7":  # Multi
                click_xy(700, 1450, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go
                click_xy(750, 1500, seconds=4)  # Click Begin Battle
            if tile == "8":  # Multi
                click_xy(800, 1225, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go
                click_xy(750, 1500, seconds=4)  # Click Begin Battle
            if tile == "9":  # Witches Den or Well
                click_xy(700, 1100, seconds=2)  # Tile
            if tile == "10":  # Single
                click_xy(550, 850, seconds=2)  # Tile
                click_xy(550, 1500, seconds=4)  # Go


# Returns result of a battle, diferent types for the different types of post-battle screens, count for number of battles in Arena
# firstOfMulti is so we don't click to clear loot after a lab battle, which would exit us from the battle screen for the second fight
def get_battle_results(type, firstOfMulti=False) -> None:
    counter = 0

    if type == "BoB":
        while counter < 30:
            if is_visible("labels/victory"):
                # logger.info('    Battle of Blood Victory!')
                click_xy(550, 1850, seconds=3)  # Clear window
                return True
            if is_visible("labels/defeat"):
                # logger.error('    Battle of Blood Defeat!')
                click_xy(550, 1850, seconds=3)  # Clear window
                return False
            counter += 1
        logger.error("Battletimer expired")
        recover()
        return False

    # Here we don't clear the result by clicking at the bottom as there is the battle report there
    if type == "HoE":
        while counter < 10:
            # Clear Rank Up message
            if is_visible(
                "labels/hoe_ranktrophy", retry=5, region=(150, 900, 350, 250)
            ):
                click_xy(550, 1200)
            if is_visible("labels/victory"):
                # logger.info('    Battle of Blood Victory!')
                click_xy(550, 700, seconds=3)  # Clear window
                return True
            if is_visible("labels/defeat"):
                # logger.error('    Battle of Blood Defeat!')
                click_xy(550, 700, seconds=3)  # Clear window
                return False
            counter += 1
        logger.error("Battletimer expired")
        return False

    if type == "lab":
        while counter < 15:
            # For 'resources exceeded' message
            if is_visible("labels/notice"):
                click_xy(550, 1250)
            if is_visible("labels/victory"):
                logger.info("    Lab Battle Victory!")
                if (
                    firstOfMulti is False
                ):  # Else we exit before second battle while trying to collect loot
                    click_xy(
                        550, 1850, seconds=5
                    )  # Clear loot popup and wait for Lab to load again
                return
            if is_visible("labels/defeat"):
                # TODO Use Duras Tears so we can continue
                logger.error("    Lab Battle  Defeat! Exiting..")
                recover()
                return False
            counter += 1
        logger.error("Battletimer expired")
        recover()
        return False

    if type == "arena":
        while counter < 10:
            if is_visible("labels/rewards"):
                return True
            if is_visible("labels/defeat"):
                return False
            wait(1)
            counter += 1
        logger.error("Arena battle timed out!")
        return False

    if type == "campaign":
        if is_visible("labels/victory", confidence=0.75, retry=2):
            logger.info("    Victory!")
            return True
        elif is_visible("labels/defeat", confidence=0.8):
            logger.error("    Defeat!")
            return False
        else:
            return "Unknown"


def challenge_hoe(settings: ChallengeOpponentSettings) -> None:
    counter = 0
    errorcounter = 0
    logger.info("Battling Heroes of Esperia " + str(settings["battles"]) + " times")
    logger.warning("Note: this currently won't work in the Legends Tower")
    confirm_loc("darkforest", region=boundaries["darkforestSelect"])
    click_xy(740, 1050)  # Open Arena of Heroes
    click_xy(550, 50)  # Clear Tickets Popup
    if is_visible("labels/heroesofesperia", click=True, seconds=3):
        # Check if we've opened it yet
        if is_visible("buttons/join_hoe", 0.8, retry=3, region=(420, 1780, 250, 150)):
            logger.warning("Heroes of Esperia not opened! Entering..")
            click_xy(550, 1850)  # Clear Info
            click_xy(550, 1850, seconds=6)  # Click join
            click_xy(550, 1140, seconds=3)  # Clear Placement
            click_xy(1000, 1650, seconds=8)  # Collect all and wait for scroll
            click_xy(550, 260, seconds=5)  # Character portrait to clear Loot
            click_xy(550, 260, seconds=5)  # Character portrait to scroll back up
        # Start battles
        if is_visible(
            "buttons/fight_hoe",
            retry=10,
            seconds=3,
            click=True,
            region=(400, 200, 400, 1500),
        ):
            while counter < settings["battles"]:
                select_opponent(choice=settings["opponent_number"], hoe=True)
                if is_visible(
                    "labels/hoe_buytickets", region=(243, 618, 600, 120)
                ):  # Check for ticket icon pixel
                    logger.error("Ticket Purchase screen found, exiting")
                    recover()
                    return
                while is_visible(
                    "buttons/heroclassselect", region=boundaries["heroclassselect"]
                ):  # This is rather than Battle button as that is animated and hard to read
                    click_xy(550, 1800, seconds=0)
                click_while_visible(
                    "buttons/skip", confidence=0.8, region=boundaries["skipAoH"]
                )
                if get_battle_results(type="HoE"):
                    logger.info("    Battle #" + str(counter + 1) + " Victory!")
                else:
                    logger.error("    Battle #" + str(counter + 1) + " Defeat!")

                # Lots of things/animations can happen after a battle so we keep clicking until we see the fight button again
                while not is_visible(
                    "buttons/fight_hoe",
                    seconds=3,
                    click=True,
                    region=(400, 200, 400, 1500),
                ):
                    if errorcounter < 6:
                        click_xy(420, 50)  # Neutral location
                        click_xy(550, 1420)  # Rank up confirm button
                        errorcounter += 1
                    else:
                        logger.error("Something went wrong post-battle, recovering")
                        recover()
                        return
                errorcounter = 0
                counter += 1
        else:
            logger.error("Heroes of Esperia Fight button not found! Recovering")
            recover()
            return
        click("buttons/exitmenu", region=boundaries["exitAoH"])
        logger.info("    Collecting Quests")
        click_xy(975, 300, seconds=2)  # Bounties
        click_xy(975, 220, seconds=2)  # Quests
        click_xy(850, 880, seconds=2)  # Top daily quest
        click_xy(550, 420, seconds=2)  # Click to clear loot
        click_xy(870, 1650, seconds=2)  # Season quests tab
        click_xy(850, 880, seconds=2)  # Top season quest
        click_xy(550, 420, seconds=2)  # Click to clear loot
        click("buttons/exitmenu", region=boundaries["exitAoH"], seconds=2)
        if check_pixel(550, 1850, 2) > 150:
            logger.info("    Collecting Heroes of Esperia Pass loot")
            click_xy(550, 1800, seconds=2)  # Collect all at the pass screen
            click_xy(420, 50)  # Click to clear loot
        click("buttons/back", retry=3, region=boundaries["backMenu"])
        click("buttons/back", retry=3, region=boundaries["backMenu"])
        click("buttons/back", retry=3, region=boundaries["backMenu"])
        logger.info("    Heroes of Esperia battles complete")
    else:
        logger.error("Heroes of Esperia not found, attempting to recover")
        recover()
