import type { PayloadAction } from "@reduxjs/toolkit";
import { createAppSlice } from "./createAppSlice";
import type { Setting, SettingValue } from "./setting";

export enum TaskType {
  ARENA_OF_HEROES = "ARENA_OF_HEROES",
  BOUNTY_BOARD = "BOUNTY_BOARD",
  EVENT = "EVENT",
  GENERAL = "GENERAL",
  GUILD = "GUILD",
  PUSH = "PUSH",
}
export interface Task {
  name: Readonly<string>;
  type: Readonly<TaskType>;
  defaultIsSelected: Readonly<boolean>;
  isSelected: boolean;
  disabled?: Readonly<boolean>;
  settings?: Readonly<Array<Setting>>;
}

export type TaskSliceState = Task[];

const numberOfBattlesSetting = (num: number) => ({
  name: "Number of battles",
  value: num,
});
const pushSettings = (): Setting[] => [
  {
    name: "Which formation",
    value: 1,
  },
  {
    name: "Copy artifacts",
    value: false,
  },
];

// TODO: Load into db so we can make task groups
const initialState: TaskSliceState = [
  {
    name: "Collect AFK rewards",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Collect fast rewards",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
    settings: [
      {
        name: "Times",
        value: 5,
      },
    ],
  },
  {
    name: "Collect mentorship points",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    name: "Assign mentor task",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    name: "Send & receive companion points",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Auto-lend mercs",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Collect mail",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },

  {
    name: "Attempt campaign",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Push campaign",
    type: TaskType.PUSH,
    settings: pushSettings(),
    defaultIsSelected: false,
    isSelected: false,
  },

  {
    name: "Collect and dispatch event bounties",
    type: TaskType.BOUNTY_BOARD,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Collect and dispatch solo bounties",
    type: TaskType.BOUNTY_BOARD,
    defaultIsSelected: true,
    isSelected: true,
    settings: [
      {
        name: "Dispatch dust",
        value: true,
      },
      {
        name: "Dispatch diamonds",
        value: true,
      },
      {
        name: "Dispatch juice",
        value: true,
      },
      {
        name: "Dispatch shards",
        value: false,
      },
      {
        name: "Max refreshes",
        value: 5,
      },
      {
        name: "Number remaining to dispatch all",
        value: 1,
      },
    ],
  },
  {
    name: "Collect and dispatch team bounties",
    type: TaskType.BOUNTY_BOARD,
    defaultIsSelected: true,
    isSelected: true,
  },

  {
    name: "Attempt King's Tower",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Push King's Tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    settings: pushSettings(),
  },
  {
    name: "Push LB tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
    settings: pushSettings(),
  },
  {
    name: "Push mauler tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
    settings: pushSettings(),
  },
  {
    name: "Push wilder tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
    settings: pushSettings(),
  },
  {
    name: "Push GB tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    settings: pushSettings(),
  },
  {
    name: "Push cele tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
    settings: pushSettings(),
  },
  {
    name: "Push hypo tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    settings: pushSettings(),
  },

  {
    name: "Run Lab",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },

  {
    name: "Dispatch treasure vanguard",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
    settings: [
      {
        name: "Operation",
        value: "Occupy",
        options: ["Escort", "Inspect", "Occupy"],
      },
      // Escort: 3 teams of 5
      {
        name: "Escort resource",
        value: "Materials",
        options: ["Food", "Materials", "Equipment"],
      },
      // Inspect: 7 teams of 3
      {
        name: "Inspect faction",
        value: 1,
        options: [1, 2, 3],
      },
      // Occupy: 7 teams of 5
      // Bonus: OCR formation names and select one
      // {
      //     name: "Formation name",
      //     value: ""
      // }
    ],
  },
  {
    name: "Purchase treasure bonds",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    name: "Collect treasure commander rewards",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    name: "Collect Task Hall rewards",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },

  {
    name: "Challenge Heroes of Esperia",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    settings: [numberOfBattlesSetting(10)],
  },
  {
    name: "Collect TS rewards",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Challenge Arena of Heroes",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: true,
    isSelected: true,
    settings: [
      numberOfBattlesSetting(1),
      {
        name: "Opponent number",
        value: 1,
        options: [1, 2, 3, 4],
      },
    ],
  },
  {
    name: "Collect gladiator coins",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: true,
    isSelected: true,
  },
  // OCR would be nice here. Pick the lower badge number
  {
    name: "Bet on Legends' Championship",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },

  {
    name: "Collect Fountain of Time",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
  },

  {
    name: "Make store purchases",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
    // TODO: Custom slot for this one
    settings: [
      {
        name: "Times",
        value: 3,
      },
      {
        name: "Use quick buy",
        value: true,
      },
      {
        name: "Shards (gold)",
        value: true,
      },
      {
        name: "Dust (gold)",
        value: true,
      },
      {
        name: "Silver emblems (gold)",
        value: false,
      },
      {
        name: "Gold emblems (gold)",
        value: false,
      },
      {
        name: "Poe (gold)",
        value: true,
      },
      {
        name: "Timegazer card (diamonds)",
        value: true,
      },
      {
        name: "Arcane staffs (diamonds)",
        value: true,
      },
      {
        name: "Baits (diamonds)",
        value: false,
      },
      {
        name: "Cores (diamonds)",
        value: false,
      },
      {
        name: "Dust (diamonds)",
        value: true,
      },
      {
        name: "Elite soulstone (diamonds)",
        value: false,
      },
      {
        name: "Superb soulstone (diamonds)",
        value: false,
      },
    ],
  },

  {
    name: "Upgrade resonating crystal",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    name: "Level up Elder Tree",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
    settings: [
      {
        name: "Branch",
        value: "Mage",
        options: ["Support", "Mage", "Warrior", "Tank", "Ranger"],
      },
    ],
  },

  {
    name: "Battle guild hunts",
    type: TaskType.GUILD,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Battle Twisted Realm",
    type: TaskType.GUILD,
    defaultIsSelected: true,
    isSelected: true,
    // settings: [
    //   {
    //     name: "Number of battles",
    //     value: 1,
    //     options: [1, "All"],
    //   },
    // ],
  },

  {
    name: "Collect daily/weekly quests",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    name: "Collect merchant deals/nobles",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },

  {
    name: "Circus tour",
    type: TaskType.EVENT,
    defaultIsSelected: false,
    isSelected: false,
  },
  {
    name: "Battle of blood",
    type: TaskType.EVENT,
    defaultIsSelected: false,
    isSelected: false,
    settings: [numberOfBattlesSetting(3)],
  },
  {
    name: "Fight of fates",
    type: TaskType.EVENT,
    defaultIsSelected: false,
    isSelected: false,
    settings: [numberOfBattlesSetting(3)],
  },

  {
    name: "Use bag consumables",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
  },
];

export const taskSlice = createAppSlice({
  name: "task",
  initialState,

  reducers: (create) => ({
    setIsSelected: create.reducer(
      (state, action: PayloadAction<{ name: string; isSelected: boolean }>) => {
        const task = state.find((task) => task.name === action.payload.name);
        if (task) task.isSelected = action.payload.isSelected;
      },
    ),

    setIsAllSelected: create.reducer(
      (state, action: PayloadAction<{ isSelected: boolean }>) => {
        for (let i = 0; i < state.length; i++) {
          state[i].isSelected = !state[i].disabled && action.payload.isSelected;
        }
        // state.forEach(
        //   (task) =>
        //     (task.isSelected = !task.disabled && action.payload.isSelected),
        // );
      },
    ),

    setSettingValue: create.reducer(
      (
        state,
        action: PayloadAction<{
          taskName: string;
          settingName: string;
          value: SettingValue;
        }>,
      ) => {
        // TODO: Extract function find by task name
        const task = state.find(
          (task) => task.name === action.payload.taskName,
        );
        const setting = task?.settings?.find(
          (setting) => setting.name === action.payload.settingName,
        );
        if (setting) setting.value = action.payload.value;
      },
    ),
  }),
});

export const { setIsSelected, setIsAllSelected, setSettingValue } =
  taskSlice.actions;
