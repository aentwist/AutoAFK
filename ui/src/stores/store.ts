import type { Action, ThunkAction } from "@reduxjs/toolkit";
import { combineSlices, configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";
import hash from "object-hash";
import { messageSlice } from "./message";
import type { Setting } from "./setting";
import { settingSlice } from "./setting";
import type { Task } from "./task";
import { taskSlice } from "./task";

// `combineSlices` automatically combines the reducers using
// their `reducerPath`s, therefore we no longer need to call `combineReducers`.
const rootReducer = combineSlices(taskSlice, settingSlice, messageSlice);
// Infer the `RootState` type from the root reducer
export type RootState = ReturnType<typeof rootReducer>;

// The store setup is wrapped in `makeStore` to allow reuse
// when setting up tests that need the same store config
export const makeStore = (preloadedState?: Partial<RootState>) => {
  const store = configureStore({
    reducer: rootReducer,
    // Adding the api middleware enables caching, invalidation, polling,
    // and other useful features of `rtk-query`.
    middleware: (getDefaultMiddleware) => {
      //   return getDefaultMiddleware().concat(quotesApiSlice.middleware)
      return getDefaultMiddleware();
    },
    preloadedState,
  });
  // configure listeners using the provided defaults
  // optional, but required for `refetchOnFocus`/`refetchOnReconnect` behaviors
  setupListeners(store.dispatch);
  return store;
};

type Store = ReturnType<typeof makeStore>;
export async function asyncMakeStore(): Promise<Store> {
  const preloadedState = await window.electronApi?.loadState();
  if (preloadedState) {
    const initialState: Partial<RootState> = {
      task: taskSlice.getInitialState(),
      setting: settingSlice.getInitialState(),
    };
    syncState(preloadedState, initialState);
  }
  const store = makeStore(preloadedState);
  store.subscribe(() => {
    const { task, setting } = store.getState();
    window.electronApi?.saveState({
      task,
      setting,
    });
  });
  return store;
}

// Only exported for testing
export function syncState(
  preloadedState: Partial<RootState>,
  initialState: Partial<RootState>,
): void {
  const ops = {
    // Allow unordered arrays since we don't fix the order when syncing
    unorderedArrays: true,
    excludeKeys: (key: string) => key === "isSelected" || key === "value",
  };
  if (hash(preloadedState, ops) !== hash(initialState, ops)) {
    // Tasks
    if (preloadedState.task) {
      syncTasksOrSettings(preloadedState.task, initialState.task);
    }

    // Settings
    if (preloadedState.setting && initialState.setting) {
      // TODO: Typing / dynamic keys
      ["clientSettings", "automationSettings", "telegramSettings"].forEach(
        (type) =>
          syncTasksOrSettings(
            preloadedState.setting[type],
            initialState.setting[type],
          ),
      );
    }

    window.electronApi?.saveState(preloadedState);
  }
}

export function syncTasksOrSettings(
  oldElts: Task[] | Setting[],
  newElts: Task[] | Setting[],
): void {
  // Names are used as keys - if an element's name changes, then it is
  // considered to be a completely new element
  const newEltsByName = new Map<string, Task | Setting>();
  newElts.forEach((elt) => newEltsByName.set(elt.name, elt));

  const indicesToRemove: number[] = [];
  for (let i = 0; i < oldElts.length; i++) {
    const oldElt = oldElts[i];
    const newElt = newEltsByName.get(oldElt.name);

    if (!newElt) {
      // Mark for removal
      indicesToRemove.push(i);
    } else {
      // Change
      oldElts[i] = { ...newElt };
      if (oldElt.isSelected !== undefined) {
        // if is Task
        oldElts[i].isSelected = oldElt.isSelected;
        if (oldElt.settings && newElt.settings) {
          // Task settings
          syncTasksOrSettings(oldElt.settings, newElt.settings);
          oldElts[i].settings = oldElt.settings;
        }
      } else if (oldElt.value !== undefined) {
        // if is Setting
        oldElts[i].value = oldElt.value;
      }

      // Mark for not adding
      newEltsByName.delete(oldElt.name);
    }
  }

  // Remove old
  for (let i = indicesToRemove.length - 1; i >= 0; i--) {
    const idx = indicesToRemove[i];
    oldElts.splice(idx, 1);
  }

  // Add new
  newEltsByName.forEach((elt) => oldElts.push(elt));
}

// Infer the type of `store`
export type AppStore = Store;
// Infer the `AppDispatch` type from the store itself
export type AppDispatch = AppStore["dispatch"];
export type AppThunk<ThunkReturnType = void> = ThunkAction<
  ThunkReturnType,
  RootState,
  unknown,
  Action
>;
