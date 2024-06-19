// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from "electron";
import type { RootState } from "./stores";
import type { Message, RunData, SettingsData } from "./types";
import { CommandType } from "./types";

const electronApi = {
  saveState: (state: Partial<RootState>): Promise<void> =>
    ipcRenderer.invoke("save-state", state),
  loadState: (): Promise<undefined | Partial<RootState>> =>
    ipcRenderer.invoke("load-state"),

  connect: (data: SettingsData) => ipcRenderer.send(CommandType.CONNECT, data),
  run: (data: RunData) => ipcRenderer.send(CommandType.RUN, data),
  pause: (data: SettingsData) => ipcRenderer.send(CommandType.PAUSE, data),
  stop: () => ipcRenderer.send(CommandType.STOP),
  onMessage: (callback: (message: Message) => void) =>
    ipcRenderer.on("message", (_event, value: Message) => callback(value)),
  removeAllOnMessageListeners: (): void =>
    void ipcRenderer.removeAllListeners("message"),
};

declare global {
  interface Window {
    // Making this optional lets us run just the web app in the browser for
    // debugging
    electronApi?: typeof electronApi;
  }
}

contextBridge.exposeInMainWorld("electronApi", electronApi);
