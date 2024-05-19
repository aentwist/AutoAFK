import { List, ListItem } from "@mui/material";
import SettingListItem from "../components/SettingListItem";
import { useAppSelector } from "../stores";

export default function Settings() {
  const { clientSettings, automationSettings, telegramSettings } = useAppSelector(
    (state) => state.setting,
  );

  return (
    <main className="flex">
      <nav className="w-1/4 px-4 border-e">
        <List>
          <ListItem component="a" href="#client">
            Client
          </ListItem>
          <ListItem component="a" href="#automation">
            Automation
          </ListItem>
          <ListItem component="a" href="#telegram">
            Telegram
          </ListItem>
        </List>
      </nav>

      <div className="overflow-y-auto scroll-smooth grow">
        <section>
          <h3 id="client" className="m-4 mb-1 text-lg uppercase">
            Client
          </h3>
          <List disablePadding>
            {clientSettings.map((setting) => (
              <SettingListItem key={setting.name} setting={setting} />
            ))}
          </List>
        </section>

        <section>
          <h3 id="automation" className="m-4 mb-1 text-lg uppercase">
            Automation
          </h3>
          <List disablePadding>
            {automationSettings.map((setting) => (
              <SettingListItem key={setting.name} setting={setting} />
            ))}
          </List>
        </section>

        <section>
          <h3 id="telegram" className="m-4 mb-1 text-lg uppercase">
            Telegram
          </h3>
          <List disablePadding>
            {telegramSettings.map((setting) => (
              <SettingListItem key={setting.name} setting={setting} />
            ))}
          </List>
        </section>
      </div>
    </main>
  );
}
