import type { PayloadAction } from "@reduxjs/toolkit";
import { Temporal } from "temporal-polyfill";
import { createAppSlice } from "./createAppSlice";
import type { Setting, SettingValue } from "./setting";

export enum TaskType {
  ARENA_OF_HEROES = "ARENA_OF_HEROES",
  EVENT = "EVENT",
  GENERAL = "GENERAL",
  GUILD = "GUILD",
  PUSH = "PUSH",
}
export interface Task {
  fn: Readonly<string>;
  name: Readonly<string>;
  type: Readonly<TaskType>;
  defaultIsSelected: Readonly<boolean>;
  isSelected: boolean;
  disabled?: Readonly<boolean>;
  settings?: Readonly<Array<Setting>>;
}

export type TaskSliceState = Task[];

// TODO: Move / use this. Towers should be disabled if not available.
enum Tower {
  LB,
  MAULER,
  WILDER,
  GB,
  CELE,
  HYPO,
}
// Which towers are open, Monday-Sunday
const TOWERS_BY_DAY = [
  [Tower.LB],
  [Tower.MAULER],
  [Tower.WILDER, Tower.CELE],
  [Tower.GB, Tower.HYPO],
  [Tower.LB, Tower.MAULER, Tower.CELE],
  [Tower.WILDER, Tower.GB, Tower.HYPO],
  [Tower.LB, Tower.MAULER, Tower.WILDER, Tower.GB, Tower.CELE, Tower.HYPO],
];
const isTowerOpen = (tower: Tower): boolean => {
  // > between 1 and 7, inclusive, with Monday being 1, and Sunday 7
  // See https://tc39.es/proposal-temporal/docs/plaindate.html#dayOfWeek
  const dayIdx = Temporal.Now.plainDateISO("UTC").dayOfWeek - 1;
  return TOWERS_BY_DAY[dayIdx].includes(tower);
};

const numberOfBattlesSetting = (num: number) => ({
  key: "battles",
  name: "Number of battles",
  value: num,
});
const opponentNumberSetting = () => ({
  key: "opponent_number",
  name: "Opponent number",
  value: 1,
  options: [1, 2, 3, 4],
});
const pushSettings = (): Setting[] => [
  {
    key: "formation",
    name: "Which formation",
    value: 1,
  },
  {
    key: "copy_artifacts",
    name: "Copy artifacts",
    value: false,
  },
];

// TODO: Load into db so we can make task groups
const initialState: TaskSliceState = [
  {
    fn: "collect_afk_rewards",
    name: "Collect AFK rewards",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    fn: "collect_fast_rewards",
    name: "Collect fast rewards",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
    settings: [
      {
        key: "times",
        name: "Times",
        value: 5,
      },
    ],
  },
  {
    fn: "collect_mentorship_points",
    name: "Collect mentorship points",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    fn: "assign_mentor_task",
    name: "Assign mentor task",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    fn: "send_and_receive_companion_points",
    name: "Send & receive companion points",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    fn: "auto_lend_mercs",
    name: "Auto-lend mercs",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    fn: "collect_mail",
    name: "Collect mail",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },

  {
    fn: "attempt_campaign",
    name: "Attempt campaign",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    fn: "push_campaign",
    name: "Push campaign",
    type: TaskType.PUSH,
    settings: pushSettings(),
    defaultIsSelected: false,
    isSelected: false,
  },

  {
    fn: "dispatch_bounties",
    name: "Collect and dispatch bounties",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
    settings: [
      {
        key: "event_bounties",
        name: "Dispatch event bounties",
        value: true,
      },
      {
        key: "solo_bounties",
        name: "Dispatch solo bounties",
        value: true,
      },
      {
        key: "team_bounties",
        name: "Dispatch team bounties",
        value: true,
      },

      {
        key: "dust",
        name: "Dispatch dust",
        value: true,
      },
      {
        key: "diamonds",
        name: "Dispatch diamonds",
        value: true,
      },
      {
        key: "juice",
        name: "Dispatch juice",
        value: true,
      },
      {
        key: "shards",
        name: "Dispatch shards",
        value: false,
      },
      {
        key: "max_refreshes",
        name: "Max refreshes",
        value: 5,
      },
      {
        key: "number_remaining_to_dispatch_all",
        name: "Number remaining to dispatch all",
        value: 1,
      },
    ],
  },

  {
    fn: "attempt_kt",
    name: "Attempt King's Tower",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    fn: "push_kt",
    name: "Push King's Tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    settings: pushSettings(),
  },
  {
    fn: "push_lb_tower",
    name: "Push LB tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: !isTowerOpen(Tower.LB),
    settings: pushSettings(),
  },
  {
    fn: "push_mauler_tower",
    name: "Push mauler tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: !isTowerOpen(Tower.MAULER),
    settings: pushSettings(),
  },
  {
    fn: "push_wilder_tower",
    name: "Push wilder tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: !isTowerOpen(Tower.WILDER),
    settings: pushSettings(),
  },
  {
    fn: "push_gb_tower",
    name: "Push GB tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: !isTowerOpen(Tower.GB),
    settings: pushSettings(),
  },
  {
    fn: "push_cele_tower",
    name: "Push cele tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: !isTowerOpen(Tower.CELE),
    settings: pushSettings(),
  },
  {
    fn: "push_hypo_tower",
    name: "Push hypo tower",
    type: TaskType.PUSH,
    defaultIsSelected: false,
    isSelected: false,
    disabled: !isTowerOpen(Tower.HYPO),
    settings: pushSettings(),
  },

  {
    fn: "run_lab",
    name: "Run Lab",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },

  {
    fn: "dispatch_treasure_vanguard",
    name: "Dispatch treasure vanguard",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
    settings: [
      {
        key: "operation",
        name: "Operation",
        value: "Occupy",
        options: ["Escort", "Inspect", "Occupy"],
      },
      // Escort: 3 teams of 5
      {
        key: "escort_rss",
        name: "Escort resource",
        value: "Materials",
        options: ["Food", "Materials", "Equipment"],
      },
      // Inspect: 7 teams of 3
      {
        key: "inspect_faction",
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
    fn: "purchase_treasure_bonds",
    name: "Purchase treasure bonds",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    fn: "collect_treasure_commander_rewards",
    name: "Collect treasure commander rewards",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    fn: "collect_task_hall_rewards",
    name: "Collect Task Hall rewards",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },

  {
    fn: "challenge_hoe",
    name: "Challenge Heroes of Esperia",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    settings: [numberOfBattlesSetting(10), opponentNumberSetting()],
  },
  {
    fn: "collect_ts_rewards",
    name: "Collect TS rewards",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    fn: "challenge_arena",
    name: "Challenge Arena of Heroes",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: true,
    isSelected: true,
    settings: [numberOfBattlesSetting(1), opponentNumberSetting()],
  },
  {
    fn: "collect_gladiator_coins",
    name: "Collect gladiator coins",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: true,
    isSelected: true,
  },
  // OCR would be nice here. Pick the lower badge number
  {
    fn: "bet_on_lc",
    name: "Bet on Legends' Championship",
    type: TaskType.ARENA_OF_HEROES,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },

  {
    fn: "collect_fountain_of_time",
    name: "Collect Fountain of Time",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
  },

  {
    fn: "make_store_purchases",
    name: "Make store purchases",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
    // TODO: Custom slot for this one
    settings: [
      {
        key: "times",
        name: "Times",
        value: 3,
      },
      {
        key: "quick_buy",
        name: "Use quick buy",
        value: true,
      },
      {
        key: "gold__shards",
        name: "Shards (gold)",
        value: true,
      },
      {
        key: "gold__dust",
        name: "Dust (gold)",
        value: true,
      },
      {
        key: "gold__silver_emblems",
        name: "Silver emblems (gold)",
        value: false,
      },
      {
        key: "gold__gold_emblems",
        name: "Gold emblems (gold)",
        value: false,
      },
      {
        key: "gold__poe",
        name: "Poe (gold)",
        value: true,
      },
      {
        key: "diamonds__timegazer",
        name: "Timegazer card (diamonds)",
        value: true,
      },
      {
        key: "diamonds__staffs",
        name: "Arcane staffs (diamonds)",
        value: true,
      },
      {
        key: "diamonds__baits",
        name: "Baits (diamonds)",
        value: false,
      },
      {
        key: "diamonds__cores",
        name: "Cores (diamonds)",
        value: false,
      },
      {
        key: "diamonds__dust",
        name: "Dust (diamonds)",
        value: true,
      },
      {
        key: "diamonds__elite_soulstone",
        name: "Elite soulstone (diamonds)",
        value: false,
      },
      {
        key: "diamonds__superb_soulstone",
        name: "Superb soulstone (diamonds)",
        value: false,
      },
    ],
  },

  {
    fn: "upgrade_rc",
    name: "Upgrade resonating crystal",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
  },
  {
    fn: "level_up_tree",
    name: "Level up Elder Tree",
    type: TaskType.GENERAL,
    defaultIsSelected: false,
    isSelected: false,
    disabled: true,
    settings: [
      {
        key: "branch",
        name: "Branch",
        value: "Mage",
        options: ["Support", "Mage", "Warrior", "Tank", "Ranger"],
      },
    ],
  },
  {
    fn: "collect_inn_gifts",
    name: "Collect Inn gifts",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },

  {
    fn: "battle_guild_hunts",
    name: "Battle guild hunts",
    type: TaskType.GUILD,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    fn: "battle_tr",
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
    fn: "collect_quests",
    name: "Collect daily/weekly quests",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },
  {
    fn: "collect_merchants",
    name: "Collect merchant deals/nobles",
    type: TaskType.GENERAL,
    defaultIsSelected: true,
    isSelected: true,
  },

  {
    fn: "circus_tour",
    name: "Circus tour",
    type: TaskType.EVENT,
    defaultIsSelected: false,
    isSelected: false,
    settings: [numberOfBattlesSetting(3)],
  },
  {
    fn: "battle_of_blood",
    name: "Battle of blood",
    type: TaskType.EVENT,
    defaultIsSelected: false,
    isSelected: false,
    settings: [numberOfBattlesSetting(3)],
  },
  {
    fn: "fight_of_fates",
    name: "Fight of fates",
    type: TaskType.EVENT,
    defaultIsSelected: false,
    isSelected: false,
    settings: [numberOfBattlesSetting(3)],
  },

  {
    fn: "use_bag_consumables",
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

  selectors: {
    selectTaskData: (tasks, taskName) => {
      const task = tasks.find((task) => task.name === taskName);
      if (!task) return undefined;

      const taskData = {
        fn: task.fn,
        name: task.name,
      };
      if (task.settings) {
        const s: Record<string, SettingValue> = {};
        task.settings.forEach((setting) => (s[setting.key] = setting.value));
        taskData.settings = s;
      }

      return taskData;
    },

    selectSelectedTaskData: (tasks) =>
      tasks
        .filter((task) => task.isSelected)
        .map((task) => {
          const taskData = {
            fn: task.fn,
            name: task.name,
          };
          if (task.settings) {
            const s: Record<string, SettingValue> = {};
            task.settings.forEach(
              (setting) => (s[setting.key] = setting.value),
            );
            taskData.settings = s;
          }

          return taskData;
        }),
  },
});

export const { setIsSelected, setIsAllSelected, setSettingValue } =
  taskSlice.actions;
export const { selectTaskData, selectSelectedTaskData } = taskSlice.selectors;
