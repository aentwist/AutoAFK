import { app, autoUpdater, dialog } from "electron";

const SERVER = "https://hazel-khaki-seven.vercel.app";
const UPDATE_POLLING_INTERVAL_MS = 15 * 60 * 1000; // 15 minutes

/** Checks for and downloads updates */
export function startUpdatePolling() {
  const url = `${SERVER}/update/${process.platform}/${app.getVersion()}`;
  autoUpdater.setFeedURL({ url });
  // setInterval(() => {
  // TODO: Do NOT force users to install updates
  // See https://github.com/electron/electron/issues/16561
  // However, in the meantime it is better to force update than never update...
  autoUpdater.checkForUpdates();
  // }, UPDATE_POLLING_INTERVAL_MS);
}

export function registerUpdateHandlers() {
  autoUpdater.on("update-downloaded", (event, releaseNotes, releaseName) => {
    const dialogOpts = {
      type: "info",
      buttons: ["Restart", "Later"],
      title: "Application Update",
      message: process.platform === "win32" ? releaseNotes : releaseName,
      detail:
        "A new version has been downloaded. Restart the application to apply the updates.",
    };

    dialog.showMessageBox(dialogOpts).then((returnValue) => {
      if (returnValue.response === 0) autoUpdater.quitAndInstall();
    });
  });

  autoUpdater.on("error", (message) => {
    console.error("There was a problem updating the application");
    console.error(message);
  });
}
