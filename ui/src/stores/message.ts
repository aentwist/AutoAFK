import { PayloadAction } from "@reduxjs/toolkit";
import type { Message } from "../types";
import { createAppSlice } from "./createAppSlice";

export type MessageSliceState = Message[];

const initialState: MessageSliceState = [];

export const messageSlice = createAppSlice({
  name: "message",
  initialState,
  reducers: (create) => ({
    pushMessage: create.reducer(
      (state, action: PayloadAction<{ message: Message }>) =>
        void state.push(action.payload.message),
    ),
  }),
  selectors: {
    selectMessageLog: (messages) =>
      messages.map((msg) => `${msg.levelname}: ${msg.message}`),
  },
});

export const { pushMessage } = messageSlice.actions;
export const { selectMessageLog } = messageSlice.selectors;
