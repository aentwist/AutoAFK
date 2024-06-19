import { BrowserWindow, app, ipcMain, shell } from "electron";
import fs from "fs/promises";
import path from "path";
import { Api } from "./api";
import type { RootState } from "./stores";
import { registerUpdateHandlers, startUpdatePolling } from "./update";

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require("electron-squirrel-startup")) {
  app.quit();
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  // and load the index.html of the app.
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(
      path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`),
    );
  }

  // Open the DevTools.
  // mainWindow.webContents.openDevTools();

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  // Receive incoming messages
  Api.getInstance().registerReceivers(mainWindow);
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on("ready", () => {
  registerHandlers();
  createWindow();
  startUpdatePolling();
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.

const statePath = path.join(app.getPath("userData"), "state.json");

// Function signatures here should match those in preload.ts
function registerHandlers(): void {
  ipcMain.handle(
    "save-state",
    async (_, state: Partial<RootState>): Promise<void> => {
      await fs.writeFile(statePath, JSON.stringify(state));
    },
  );

  ipcMain.handle(
    "load-state",
    async (): Promise<undefined | Partial<RootState>> => {
      let data: string;
      try {
        data = await fs.readFile(statePath, "utf8");
      } catch (err) {
        if ((err as NodeJS.ErrnoException).code === "ENOENT") return undefined;
        throw err;
      }
      return JSON.parse(data);
    },
  );

  // Send outgoing messages
  Api.getInstance().registerCommands();

  registerUpdateHandlers();
}
