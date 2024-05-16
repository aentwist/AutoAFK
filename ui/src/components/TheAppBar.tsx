import { mdiAndroid } from "@mdi/js";
import { Icon } from "@mdi/react";
import { AppBar, Tab, Tabs, Toolbar } from "@mui/material";
import { useState } from "react";
import { Link } from "react-router-dom";
import TheMoreOptions from "./TheMoreOptions";

export default function TheAppBar() {
  const views = [
    {
      name: "Tasks",
      to: "tasks",
    },
    {
      name: "Task Groups",
      to: "task-groups",
      disabled: true,
    },
    {
      name: "Scheduler",
      to: "scheduler",
      disabled: true,
    },
    {
      name: "Console",
      to: "console",
    },
  ];
  const [tab, setTab] = useState(0);

  return (
    <AppBar position="sticky">
      <Toolbar>
        <Link className="flex" to="/">
          <Icon path={mdiAndroid} />
          <span className="ms-1 text-lg">AutoAFK</span>
        </Link>

        <Tabs
          className="mx-4 grow"
          value={tab}
          onChange={(_, t: number) => setTab(t)}
        >
          {views.map((view, i) => (
            <Tab
              key={view.name}
              className={`!leading-4 !text-inherit ${view.disabled && "brightness-75"}`}
              label={view.name}
              value={i}
              component={Link}
              to={view.to}
              disabled={view.disabled}
            />
          ))}
        </Tabs>

        <TheMoreOptions />
      </Toolbar>
    </AppBar>
  );
}
