import { expect, test } from "vitest";
import type { RootState } from "../store";
import { syncState, syncTasksOrSettings } from "../store";

const stateTest = test.extend({
  OLD_STATE: <Partial<RootState>>{
    task: [
      {
        fn: "collect_afk_rewards",
        name: "Collect AFK rewards",
        type: "GENERAL",
        defaultIsSelected: true,
        isSelected: true,
        disabled: true,
      },
      {
        fn: "challenge_hoe",
        name: "Challenge Heroes of Esperia",
        type: "ARENA_OF_HEROES",
        defaultIsSelected: false,
        isSelected: false,
        settings: [
          { key: "battles", name: "Number of battles", value: 10 },
          {
            key: "opponent_number",
            name: "Opponent number",
            value: 1,
            options: [1, 2, 3, 4],
          },
        ],
      },
    ],
    setting: {
      clientSettings: [
        { key: "emulator_path", name: "Emulator path", value: "" },
        { key: "port", name: "Port", value: 5555 },
        { key: "debug_mode", name: "Debug mode", value: false },
      ],
      automationSettings: [
        { key: "start_delay_min", name: "Start delay (minutes)", value: 0 },
      ],
      telegramSettings: [
        { key: "enable_telegram", name: "Enable Telegram", value: false },
      ],
    },
  },

  NEW_STATE: <Partial<RootState>>{
    task: [
      {
        // fn: "collect_afk_rewards",
        fn: "foobar",
        // name: "Collect AFK rewards",
        name: "Foobar",
        type: "GENERAL",
        // defaultIsSelected: true,
        defaultIsSelected: false,
        // isSelected: true,
        isSelected: false,
        // disabled: true,
      },
      {
        // fn: "challenge_hoe",
        fn: "foobar",
        name: "Challenge Heroes of Esperia",
        type: "ARENA_OF_HEROES",
        // defaultIsSelected: false,
        defaultIsSelected: true,
        // isSelected: false,
        isSelected: true,
        settings: [
          {
            // key: "battles",
            key: "my_battles",
            name: "Number of battles",
            // value: 10,
            value: 5,
          },
          {
            key: "opponent_number",
            name: "Opponent number",
            value: 1,
            // options: [1, 2, 3, 4],
            options: [1, 2, 3, 4, 5],
          },
        ],
      },
    ],
    setting: {
      clientSettings: [
        {
          key: "emulator_path",
          // name: "Emulator path",
          name: "New emulator path",
          value: "my/path",
        },
        // { key: "port", name: "Port", value: 5555 },
        { key: "debug_mode", name: "Debug mode", value: false },
      ],
      automationSettings: [
        { key: "start_delay_min", name: "Start delay (minutes)", value: 0 },
      ],
      telegramSettings: [
        { key: "enable_telegram", name: "Enable Telegram", value: false },
      ],
    },
  },

  SYNCED_STATE: {
    task: [
      {
        fn: "foobar",
        name: "Challenge Heroes of Esperia",
        type: "ARENA_OF_HEROES",
        defaultIsSelected: true,
        isSelected: false,
        settings: [
          { key: "my_battles", name: "Number of battles", value: 10 },
          {
            key: "opponent_number",
            name: "Opponent number",
            value: 1,
            options: [1, 2, 3, 4, 5],
          },
        ],
      },
      {
        fn: "foobar",
        name: "Foobar",
        type: "GENERAL",
        defaultIsSelected: false,
        isSelected: false,
      },
    ],
    setting: {
      clientSettings: [
        { key: "debug_mode", name: "Debug mode", value: false },
        { key: "emulator_path", name: "New emulator path", value: "my/path" },
      ],
      automationSettings: [
        { key: "start_delay_min", name: "Start delay (minutes)", value: 0 },
      ],
      telegramSettings: [
        { key: "enable_telegram", name: "Enable Telegram", value: false },
      ],
    },
  },
});

stateTest(
  "syncTasksOrSettings syncs settings",
  ({ OLD_STATE, NEW_STATE, SYNCED_STATE }) => {
    syncTasksOrSettings(
      OLD_STATE.setting.clientSettings,
      NEW_STATE.setting.clientSettings,
    );
    expect(OLD_STATE.setting.clientSettings).toEqual(
      SYNCED_STATE.setting.clientSettings,
    );

    syncTasksOrSettings(
      OLD_STATE.setting.automationSettings,
      NEW_STATE.setting.automationSettings,
    );
    expect(OLD_STATE.setting.automationSettings).toEqual(
      SYNCED_STATE.setting.automationSettings,
    );
  },
);

stateTest(
  "syncTasksOrSettings syncs tasks and their settings",
  ({ OLD_STATE, NEW_STATE, SYNCED_STATE }) => {
    syncTasksOrSettings(OLD_STATE.task, NEW_STATE.task);
    expect(OLD_STATE.task).toEqual(SYNCED_STATE.task);
  },
);

stateTest("syncState syncs state", ({ OLD_STATE, NEW_STATE, SYNCED_STATE }) => {
  syncState(OLD_STATE, NEW_STATE);
  expect(OLD_STATE).toEqual(SYNCED_STATE);
});
