import { createMemoryRouter } from "react-router-dom";
import App from "./App";
import Console from "./views/Console";
import Error from "./views/Error";
import Home from "./views/Home";
import Scheduler from "./views/Scheduler";
import Settings from "./views/Settings";
import TaskGroups from "./views/TaskGroups";
import Tasks from "./views/Tasks";

const router = createMemoryRouter([
  {
    element: <App />,
    errorElement: <Error />,
    children: [
      {
        path: "/",
        element: <Home />,
      },
      {
        path: "tasks",
        element: <Tasks />,
      },
      {
        path: "task-groups",
        element: <TaskGroups />,
      },
      {
        path: "scheduler",
        element: <Scheduler />,
      },
      {
        path: "console",
        element: <Console />,
      },
      {
        path: "settings",
        element: <Settings />,
      },
    ],
  },
]);

export default router;
