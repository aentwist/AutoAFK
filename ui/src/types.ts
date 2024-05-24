// Common types must not be defined on the Electron side - if the module they
// are in uses Node imports and the React side accesses that, it won't work

import type { SettingValue } from "./stores/setting";

// Outgoing

export enum CommandType {
  CONNECT = "CONNECT",
  RUN = "RUN",
  PAUSE = "PAUSE",
  STOP = "STOP",
}

export type CommandData = Record<string, unknown>;

export type AppSettings = Record<string, SettingValue>;

export interface SettingsData extends CommandData {
  app_settings: AppSettings;
}

// Transformed version of normal tasks
export interface TaskData {
  fn: string;
  name: string;
  settings: AppSettings;
}

export interface RunData extends SettingsData {
  tasks: TaskData[];
}

// Incoming

export enum MessageLevel {
  DEBUG = "DEBUG",
  INFO = "INFO",
  WARNING = "WARNING",
  ERROR = "ERROR",
}

export interface Message {
  levelname: MessageLevel;
  message: string;
}
