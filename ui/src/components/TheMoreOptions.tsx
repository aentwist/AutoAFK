import {
  mdiClose,
  mdiCogOutline,
  mdiDotsVertical,
  mdiGithub,
  mdiNoteOutline,
  mdiOpenInNew,
  mdiThemeLightDark,
} from "@mdi/js";
import Icon from "@mdi/react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Tooltip,
} from "@mui/material";
import { useState } from "react";
import { Link } from "react-router-dom";

export default function TheMoreOptions() {
  const [anchorEl, setAnchorEl] = useState<HTMLElement>();
  const close = () => setAnchorEl(undefined);

  const handleToggleTheme = () => {
    // TODO: Toggle theme
    close();
  };
  const [showAbout, setShowAbout] = useState(false);
  const handleShowAbout = () => {
    setShowAbout(true);
    close();
  };

  const optionsMenuItem = (name: string, icon: string) => (
    <>
      <ListItemIcon>
        <Icon path={icon} />
      </ListItemIcon>
      <ListItemText>{name}</ListItemText>
    </>
  );

  return (
    <>
      <Tooltip title="Options">
        <IconButton
          size="large"
          color="inherit"
          edge="end"
          onClick={(e) => setAnchorEl(e.currentTarget)}
        >
          <Icon path={mdiDotsVertical} />
        </IconButton>
      </Tooltip>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={close}>
        <MenuItem disabled>
          <ListItemButton onClick={handleToggleTheme}>
            {optionsMenuItem("Toggle theme", mdiThemeLightDark)}
          </ListItemButton>
        </MenuItem>
        <MenuItem>
          <ListItemButton component={Link} to="settings" onClick={close}>
            {optionsMenuItem("Settings", mdiCogOutline)}
          </ListItemButton>
        </MenuItem>
        <MenuItem>
          <ListItemButton
            component="a"
            href="https://discord.gg/floofpire"
            target="_blank"
            onClick={close}
          >
            {optionsMenuItem("Discord", mdiOpenInNew)}
          </ListItemButton>
        </MenuItem>
        <MenuItem>
          <ListItemButton
            component="a"
            href="https://github.com/aentwist/AutoAFK"
            target="_blank"
            onClick={close}
          >
            {optionsMenuItem("Github", mdiGithub)}
          </ListItemButton>
        </MenuItem>
        <MenuItem>
          <ListItemButton onClick={handleShowAbout}>
            {optionsMenuItem("About", mdiNoteOutline)}
          </ListItemButton>
        </MenuItem>
      </Menu>

      <Dialog
        PaperProps={{
          className: "w-1/3",
        }}
        open={showAbout}
        onClose={() => setShowAbout(false)}
      >
        <DialogTitle className="flex justify-between items-center">
          About
          <IconButton onClick={() => setShowAbout(false)}>
            <Icon path={mdiClose} />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>useful build info</DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAbout(false)}>OK</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
