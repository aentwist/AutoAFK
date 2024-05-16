import { css } from "@emotion/react";
import { useTheme } from "@mui/material";

export default function Home() {
  const {
    mixins: { toolbar },
  } = useTheme();
  const h = `calc(100vh - (${toolbar?.minHeight}px + ${8}px))`;

  // Put this bastard into a string to stop Vite minification from eating it.
  // And so it must also be escaped (\ and `).
  const welcome = `   ___        _         ___  ______ _   __
  / _ \\      | |       / _ \\ |  ___| | / /
 / /_\\ \\_   _| |_ ___ / /_\\ \\| |_  | |/ / 
 |  _  | | | | __/ _ \\|  _  ||  _| |    \\ 
 | | | | |_| | || (_) | | | || |   | |\\  \\
 \\_| |_/\\__,_|\\__\\___/\\_| |_/\\_|   \\_| \\_/`;

  return (
    <div
      className="grid place-content-center"
      css={css`
        height: ${h};
      `}
    >
      <div className="p-12 border border-current">
        <h1 className="mb-8 text-center">
          <pre className="leading-none">{welcome}</pre>
        </h1>
        <ol className="!list-inside !list-decimal text-lg" start={0}>
          <li className="my-1 py-1">Set emulator display and adb</li>
          <li className="my-1 py-1">Configure and run tasks</li>
          <li className="my-1 py-1">
            Create and run task groups from multiple tasks
          </li>
          <li className="my-1 py-1">
            Schedule task groups to run at your convenience
          </li>
        </ol>
      </div>
    </div>
  );
}
