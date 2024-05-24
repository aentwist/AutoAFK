import { mdiClose, mdiCog, mdiPlay } from "@mdi/js";
import Icon from "@mdi/react";
import {
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from "@mui/material";
import { useState } from "react";
import { useDebouncedCallback } from "use-debounce";
import { useAppDispatch, useAppSelector, useAppStore } from "../stores";
import { selectAppSettings } from "../stores/setting";
import type { Task } from "../stores/task";
import {
  selectTaskData,
  setIsSelected as setIsSelectedPersistent,
} from "../stores/task";
import SettingListItem from "./SettingListItem";

type TaskListItemProps = {
  task: Task;
};

export default function TaskListItem({ task }: TaskListItemProps) {
  const store = useAppStore();
  const dispatch = useAppDispatch();

  const [isSelected, setIsSelected] = useState(task.isSelected);
  const setIsSelectedState = useDebouncedCallback(
    (sel: boolean) =>
      dispatch(setIsSelectedPersistent({ name: task.name, isSelected: sel })),
    1000,
  );
  const handleToggleIsSelected = () => {
    const sel = !isSelected;
    setIsSelected(sel);
    setIsSelectedState(sel);
  };

  const [showSettings, setShowSettings] = useState(false);
  const closeSettings = () => setShowSettings(false);

  const taskData = useAppSelector(() =>
    selectTaskData(store.getState(), task.name),
  );
  const appSettings = useAppSelector(selectAppSettings);
  const handleRunTask = () => {
    window.electronApi?.run({ tasks: [taskData], app_settings: appSettings });
  };

  return (
    <>
      <ListItem
        secondaryAction={
          <>
            {task.settings && (
              <Tooltip title={`${task.name} settings`}>
                <IconButton
                  className="me-1"
                  disabled={task.disabled}
                  onClick={() => setShowSettings(true)}
                >
                  <Icon path={mdiCog} />
                </IconButton>
              </Tooltip>
            )}
            <Tooltip title={`Run ${task.name.toLowerCase()}`}>
              <IconButton
                edge="end"
                disabled={task.disabled}
                onClick={handleRunTask}
              >
                <Icon
                  className={task.disabled && "opacity-35"}
                  path={mdiPlay}
                  color="green"
                />
              </IconButton>
            </Tooltip>
          </>
        }
        disablePadding
      >
        <ListItemButton
          disabled={task.disabled}
          onClick={handleToggleIsSelected}
        >
          <ListItemIcon>
            <Checkbox checked={isSelected} edge="start" disableRipple />
          </ListItemIcon>
          <ListItemText primary={task.name} />
        </ListItemButton>
      </ListItem>

      <Dialog
        PaperProps={{
          className: "w-1/2",
        }}
        open={showSettings}
        onClose={closeSettings}
      >
        <DialogTitle className="flex justify-between items-center capitalize">
          {task.name} Settings
          <IconButton onClick={closeSettings}>
            <Icon path={mdiClose} />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <List>
            {task.settings?.map((setting) => (
              <SettingListItem
                key={setting.name}
                setting={setting}
                taskName={task.name}
              />
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          {/* <Button onClick={closeSettings}>
            Cancel
          </Button> */}
          <Button className="uppercase" onClick={closeSettings}>
            {/* Save */}
            Ok
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
