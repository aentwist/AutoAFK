import { css } from "@emotion/react";
import { mdiPlay } from "@mdi/js";
import Icon from "@mdi/react";
import {
  Button,
  Checkbox,
  List,
  ListItem,
  ListItemText,
  Toolbar,
  Tooltip,
  useTheme,
} from "@mui/material";
import TaskListItem from "../components/TaskListItem";
import { useAppDispatch, useAppSelector } from "../stores";
import { TaskType, setIsAllSelected } from "../stores/task";

const snakeToLowerCase = (str: string) =>
  str.replaceAll("_", " ").toLowerCase();

export default function Tasks() {
  const dispatch = useAppDispatch();

  const {
    mixins: { toolbar },
  } = useTheme();
  const offset = `calc(100vh - ${toolbar?.minHeight}px - 8px)`;
  const scrollOffset = css`
    scroll-margin-top: calc(2 * (${toolbar?.minHeight}px - 16px));
  `;

  const tasks = useAppSelector((state) => state.task);
  const isAllSelected = tasks.every((task) => task.disabled || task.isSelected);
  const handleSelectAll = () =>
    dispatch(setIsAllSelected({ isSelected: !isAllSelected }));

  // Programmatically create a list of the task types to use for the categories
  const taskTypes: string[] = [];
  for (const type in TaskType) taskTypes.push(type);
  // Move General to the first position
  for (let i = 0; i < taskTypes.length; i++) {
    if (taskTypes[i] === TaskType.GENERAL) {
      [taskTypes[0], taskTypes[i]] = [taskTypes[i], taskTypes[0]];
      break;
    }
  }

  return (
    <main className="flex">
      <nav className="w-1/4 px-4 border-e">
        <section>
          <Toolbar disableGutters component="h5" className="border-b text-lg">
            Category
          </Toolbar>
          <List>
            {taskTypes.map((type) => (
              <ListItem key={type} component="a" href={`#${type}`}>
                <ListItemText className="capitalize">
                  {snakeToLowerCase(type)}
                </ListItemText>
              </ListItem>
            ))}
          </List>
        </section>
      </nav>

      <div
        className="h-screen overflow-y-auto scroll-smooth relative grow"
        style={{ height: offset }}
      >
        <Toolbar
          className="px-1 !sticky top-0 !bg-white z-10 flex justify-between border-b"
          disableGutters
        >
          <Tooltip title="Select All">
            <Checkbox checked={isAllSelected} onClick={handleSelectAll} />
          </Tooltip>
          <Button>
            Run Selected
            <Icon path={mdiPlay} color="green" />
          </Button>
        </Toolbar>

        <div>
          {taskTypes.map((type) => (
            <section key={type}>
              <h3
                id={type}
                css={scrollOffset}
                className="m-4 uppercase text-lg"
              >
                {snakeToLowerCase(type)}
              </h3>
              <List disablePadding>
                {tasks
                  .filter((t) => t.type === type)
                  .map((t) => (
                    <TaskListItem key={t.name + t.isSelected} task={t} />
                  ))}
              </List>
            </section>
          ))}
        </div>
      </div>
    </main>
  );
}
