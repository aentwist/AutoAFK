import { Switch } from "@mui/joy";
import type { SelectChangeEvent } from "@mui/material";
import {
  ListItem,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Select,
  TextField,
} from "@mui/material";
import { useState } from "react";
import { useDebouncedCallback } from "use-debounce";
import { useAppDispatch } from "../stores";
import type { Setting, SettingValue } from "../stores/setting";
import { setValue as setSettingValue } from "../stores/setting";
import { setSettingValue as setTaskSettingValue } from "../stores/task";

type SettingListItemProps = {
  setting: Setting;
  taskName?: string;
};

export default function SettingListItem({
  setting,
  taskName,
}: SettingListItemProps) {
  const dispatch = useAppDispatch();

  const isSettingBoolean =
    typeof setting.value === "boolean" && !setting.options;

  const [value, setValue] = useState(setting.value);
  const setValueState = useDebouncedCallback((val: SettingValue) => {
    dispatch(
      taskName
        ? setTaskSettingValue({
            taskName,
            settingName: setting.name,
            value: val,
          })
        : setSettingValue({ name: setting.name, value: val }),
    );
  }, 1000);
  const handleSetValue = (e: SelectChangeEvent) => {
    const val: SettingValue = isSettingBoolean
      ? e.target.checked
      : e.target.value;
    setValue(val);
    setValueState(val);
  };

  const settingInput = (setting: Setting) => {
    // TODO: Type
    let elt;
    if (setting.options) {
      elt = (
        <Select
          label={setting.name}
          value={value as string}
          onChange={handleSetValue}
        >
          {setting.options.map((option, i) => (
            <MenuItem key={i} value={option}>
              {option}
            </MenuItem>
          ))}
        </Select>
      );
    } else if (typeof setting.value === "boolean") {
      elt = setting.name;
    } else if (typeof setting.value === "number") {
      elt = (
        <TextField
          type="number"
          fullWidth
          label={setting.name}
          value={value}
          onChange={handleSetValue}
        />
      );
    } else {
      elt = (
        <TextField
          variant="outlined"
          fullWidth
          label={setting.name}
          value={value}
          onChange={handleSetValue}
        />
      );
    }
    return elt;
  };

  return (
    <ListItem key={setting.name}>
      {isSettingBoolean && (
        <ListItemIcon>
          <Switch checked={value as boolean} onChange={handleSetValue} />
        </ListItemIcon>
      )}
      <ListItemText>
        {isSettingBoolean ? setting.name : settingInput(setting)}
      </ListItemText>
    </ListItem>
  );
}
