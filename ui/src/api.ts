import { spawn } from "child_process";
import type { BrowserWindow } from "electron";
import { app, ipcMain } from "electron";
import path from "path";
import type { CommandData, Message, RunData, SettingsData } from "./types";
import { CommandType } from "./types";

export class Api {
  private static instance = new Api();

  private bin = app.isPackaged
    ? path.join(process.resourcesPath, "main/main")
    : "../api/.venv/bin/python";
  private args = app.isPackaged ? undefined : ["../api/main.py"];
  private api;

  private constructor() {
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
