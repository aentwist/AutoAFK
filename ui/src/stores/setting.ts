import type { PayloadAction } from "@reduxjs/toolkit";
import { createAppSlice } from "./createAppSlice";

export type SettingValue = boolean | number | string;
export interface Setting {
  name: string;
  value: SettingValue;
  options?: Array<number | string>;
}

export type SettingSliceState = {
  clientSettings: Setting[];
  automationSettings: Setting[];
};

const initialState: SettingSliceState = {
  clientSettings: [
    {
      name: "Emulator path",
      value: "",
    },
    {
      name: "Port",
      value: 5555,
    },
    {
      name: "Debug mode",
      value: false,
    },
  ],
  automationSettings: [
    {
      name: "Start delay (minutes)",
      value: 0,
    },
    {
      name: "Action wait multiplier",
      value: 1,
    },
    {
      name: "Victory check frequency",
      value: 2,
    },
    {
      name: "Surpress victory check spam",
      value: true,
    },
    {
      name: "Use popular formations",
      value: true,
    },
    {
      name: "Hibernate when finished",
      value: false,
    },
  ],
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
          state.automationSettings.find(isName);
        setting!.value = action.payload.value;
      },
    ),
  }),
});

export const { setValue } = settingSlice.actions;
