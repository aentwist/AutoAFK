import { Outlet } from "react-router-dom";
import TheAppBar from "./components/TheAppBar";

export default function App() {
  return (
    <>
      <TheAppBar />
      <Outlet />
    </>
  );
}
