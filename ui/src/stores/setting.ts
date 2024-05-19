import type { PayloadAction } from "@reduxjs/toolkit";
import { createAppSlice } from "./createAppSlice";

export type SettingValue = boolean | number | string;
export interface Setting {
  key: string;
  name: string;
  value: SettingValue;
  options?: Array<number | string>;
}

export type SettingSliceState = {
  clientSettings: Setting[];
  automationSettings: Setting[];
  telegramSettings: Setting[];
};

const initialState: SettingSliceState = {
  clientSettings: [
    {
      key: "emulator_path",
      name: "Emulator path",
      value: "",
    },
    {
      key: "port",
      name: "Port",
      value: 5555,
    },
    {
      key: "debug_mode",
      name: "Debug mode",
      value: false,
    },
  ],
  automationSettings: [
    {
      key: "start_delay_min",
      name: "Start delay (minutes)",
      value: 0,
    },
    {
      key: "wait_multiplier",
      name: "Action wait multiplier",
      value: 1,
    },
    {
      key: "victory_check_freq_min",
      name: "Victory check frequency (minutes)",
      value: 2,
    },
    {
      key: "surpress_victory_check_spam",
      name: "Surpress victory check spam",
      value: true,
    },
    {
      key: "ignore_formations",
      name: "Ignore formations",
      value: true,
    },
    {
      key: "use_popular_formations",
      name: "Use popular formations",
      value: true,
    },
    {
      key: "hibernate_when_finished",
      name: "Hibernate when finished",
      value: false,
    },
  ],
  telegramSettings: [
    {
      key: "enable_telegram",
      name: "Enable Telegram",
      value: false,
    },
    {
      key: "token",
      name: "Token",
      value: "",
    },
    {
      key: "chat_id",
      name: "Chat ID",
      value: 0,
    },
  ]
};

export const settingSlice = createAppSlice({
  name: "setting",
  initialState,
  reducers: (create) => ({
    setValue: create.reducer(
      (state, action: PayloadAction<{ name: string; value: SettingValue }>) => {
        const isName = (setting: Setting) =>
          setting.name === action.payload.name;
        const setting =
          state.clientSettings.find(isName) ??
          state.automationSettings.find(isName) ??
          state.telegramSettings.find(isName);
        setting!.value = action.payload.value;
      },
    ),
  }),
});

export const { setValue } = settingSlice.actions;
