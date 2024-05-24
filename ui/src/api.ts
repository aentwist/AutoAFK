import { spawn } from "child_process";
import type { BrowserWindow } from "electron";
import { ipcMain } from "electron";
import type { CommandData, Message, RunData, SettingsData } from "./types";
import { CommandType } from "./types";

// import { dirname } from "path";
// import { fileURLToPath } from "url";

export class Api {
  private static instance = new Api();

  private bin = "../api/.venv/bin/python";
  private args = ["../api/autoafk/main.py"];
  private api;

  private constructor() {
    // TODO: Add packaged config
    // const __filename = fileURLToPath(import.meta.url);
    // const __dirname = dirname(__filename);
    // console.log(__dirname);

    this.api = spawn(this.bin, this.args);

    this.api.on("close", (code) => {
      console.log(`child process exited with code ${code}`);
    });
  }

  static getInstance() {
    return this.instance;
  }

  private send(type: CommandType, data: CommandData = {}) {
    const message = { type: type, ...data };
    this.api.stdin.write(JSON.stringify(message) + "\n");
  }

  registerCommands() {
    ipcMain.on(CommandType.CONNECT, (_, data: SettingsData) =>
      this.send(CommandType.CONNECT, data),
    );
    ipcMain.on(CommandType.RUN, (_, data: RunData) =>
      this.send(CommandType.RUN, data),
    );
    ipcMain.on(CommandType.PAUSE, (_, data: SettingsData) =>
      this.send(CommandType.PAUSE, data),
    );
    ipcMain.on(CommandType.STOP, () => this.send(CommandType.STOP));
  }

  registerReceivers(browserWindow: BrowserWindow): void {
    this.api.stdout.on("data", (data) => {
      const datas = String(data).split("\n");
      datas.pop();
      const messages = datas.map((data) => <Message>JSON.parse(data));
      messages.forEach((msg) => browserWindow.webContents.send("message", msg));
    });

    this.api.stderr.on("data", (data) => {
      const message = {
        levelname: "STDERR",
        message: String(data),
      };
      browserWindow.webContents.send("message", message);
    });
  }
}
