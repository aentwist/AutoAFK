import { useEffect } from "react";
import { Outlet } from "react-router-dom";
import TheAppBar from "./components/TheAppBar";
import { useAppDispatch } from "./stores";
import { pushMessage } from "./stores/message";

export default function App() {
  const dispatch = useAppDispatch();

  // Watch for electron events here so there are no issues with un/mounting
  useEffect(() => {
    window.electronApi?.onMessage((message) => {
      dispatch(pushMessage({ message }));
    });
    return window.electronApi?.removeAllOnMessageListeners;
  }, []);

  return (
    <>
      <TheAppBar />
      <Outlet />
    </>
  );
}
