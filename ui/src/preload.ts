// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from "electron";
import type { RootState } from "./stores";

const electronApi = {
  saveState: (state: RootState): Promise<void> =>
    ipcRenderer.invoke("save-state", state),
  loadState: (): Promise<undefined | RootState> =>
    ipcRenderer.invoke("load-state"),
};

declare global {
  interface Window {
    // Making this optional lets us run just the web app in the browser for
    // debugging
    electronApi?: typeof electronApi;
  }
}

contextBridge.exposeInMainWorld("electronApi", electronApi);
