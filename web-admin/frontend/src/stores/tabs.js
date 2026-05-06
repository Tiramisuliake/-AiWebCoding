import { ref } from "vue";
import { defineStore } from "pinia";

const HOME_TAB = {
  name: "dashboard",
  path: "/",
  titleKey: "common.dashboard",
  closable: false
};
const TABS_STATE_STORAGE_KEY = "web_admin_tabs_state_v1";

function normalizePath(path) {
  if (typeof path !== "string") {
    return "";
  }
  return path.trim();
}

function normalizePathForPermission(path) {
  const normalized = normalizePath(path);
  if (!normalized) {
    return "";
  }
  return normalized.split("#")[0].split("?")[0] || normalized;
}

function toTabRecord(rawTab) {
  if (!rawTab || typeof rawTab !== "object") {
    return null;
  }

  const name = String(rawTab.name || "").trim();
  if (!name) {
    return null;
  }
  if (name === HOME_TAB.name) {
    return { ...HOME_TAB };
  }

  const path = normalizePath(rawTab.path);
  if (!path) {
    return null;
  }

  const titleKey =
    typeof rawTab.titleKey === "string" && rawTab.titleKey.trim()
      ? rawTab.titleKey.trim()
      : `route.${name}`;

  return {
    name,
    path,
    titleKey,
    closable: true
  };
}

function sanitizeState(rawTabs, rawActiveName, canAccessPath) {
  const pathGuard = typeof canAccessPath === "function" ? canAccessPath : () => true;
  const dedupedTabs = [{ ...HOME_TAB }];
  const seen = new Set([HOME_TAB.name]);

  for (const rawTab of Array.isArray(rawTabs) ? rawTabs : []) {
    const tab = toTabRecord(rawTab);
    if (!tab || seen.has(tab.name)) {
      continue;
    }

    const pathForGuard = normalizePathForPermission(tab.path);
    if (!pathForGuard || !pathGuard(pathForGuard)) {
      continue;
    }

    seen.add(tab.name);
    dedupedTabs.push(tab);
  }

  const expectedActive = String(rawActiveName || HOME_TAB.name);
  const nextActiveName = dedupedTabs.some((tab) => tab.name === expectedActive)
    ? expectedActive
    : HOME_TAB.name;

  return {
    tabs: dedupedTabs,
    activeName: nextActiveName
  };
}

export const useTabsStore = defineStore("tabs", () => {
  const tabs = ref([{ ...HOME_TAB }]);
  const activeName = ref(HOME_TAB.name);

  function persistTabs() {
    const payload = {
      tabs: tabs.value.map((tab) => ({
        name: tab.name,
        path: tab.path,
        titleKey: tab.titleKey,
        closable: tab.closable !== false
      })),
      activeName: activeName.value
    };
    localStorage.setItem(TABS_STATE_STORAGE_KEY, JSON.stringify(payload));
  }

  function sanitizeTabs(options = {}) {
    const { canAccessPath } = options;
    const nextState = sanitizeState(tabs.value, activeName.value, canAccessPath);
    tabs.value = nextState.tabs;
    activeName.value = nextState.activeName;
    persistTabs();
  }

  function hydrateTabs(options = {}) {
    const { canAccessPath } = options;
    const raw = localStorage.getItem(TABS_STATE_STORAGE_KEY);
    if (!raw) {
      sanitizeTabs({ canAccessPath });
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      const nextState = sanitizeState(parsed?.tabs, parsed?.activeName, canAccessPath);
      tabs.value = nextState.tabs;
      activeName.value = nextState.activeName;
      persistTabs();
    } catch (_error) {
      localStorage.removeItem(TABS_STATE_STORAGE_KEY);
      sanitizeTabs({ canAccessPath });
    }
  }

  function ensureTab(route) {
    if (!route?.name || route.meta?.tab === false) {
      return;
    }

    const name = String(route.name);
    const tab = {
      name,
      path: route.fullPath,
      titleKey: route.meta?.titleKey || `route.${name}`,
      closable: name !== HOME_TAB.name
    };

    const index = tabs.value.findIndex((item) => item.name === name);
    if (index === -1) {
      tabs.value.push(tab);
    } else {
      tabs.value[index] = tab;
    }
    activeName.value = name;
    persistTabs();
  }

  function removeTab(name) {
    const targetIndex = tabs.value.findIndex((item) => item.name === name);
    if (targetIndex === -1) {
      return tabs.value.find((item) => item.name === activeName.value)?.path || HOME_TAB.path;
    }

    const removed = tabs.value[targetIndex];
    if (!removed.closable) {
      return removed.path;
    }

    tabs.value.splice(targetIndex, 1);

    if (activeName.value !== removed.name) {
      persistTabs();
      return tabs.value.find((item) => item.name === activeName.value)?.path || HOME_TAB.path;
    }

    const fallback = tabs.value[targetIndex - 1] || tabs.value[targetIndex] || tabs.value[0];
    activeName.value = fallback?.name || HOME_TAB.name;
    persistTabs();
    return fallback?.path || HOME_TAB.path;
  }

  function closeOthers(name) {
    const keep = tabs.value.find((item) => item.name === name) || HOME_TAB;
    tabs.value = [tabs.value.find((item) => item.name === HOME_TAB.name) || HOME_TAB];
    if (keep.name !== HOME_TAB.name) {
      tabs.value.push(keep);
    }
    activeName.value = keep.name;
    persistTabs();
    return keep.path;
  }

  function closeAll() {
    tabs.value = [{ ...HOME_TAB }];
    activeName.value = HOME_TAB.name;
    persistTabs();
    return HOME_TAB.path;
  }

  function reorderClosableTabs(oldDraggableIndex, newDraggableIndex) {
    const from = Number(oldDraggableIndex);
    const to = Number(newDraggableIndex);

    if (!Number.isInteger(from) || !Number.isInteger(to) || from === to) {
      return;
    }

    const closableTabIndexes = tabs.value.reduce((indexes, tab, index) => {
      if (tab.closable) {
        indexes.push(index);
      }
      return indexes;
    }, []);

    if (
      from < 0 ||
      to < 0 ||
      from >= closableTabIndexes.length ||
      to >= closableTabIndexes.length
    ) {
      return;
    }

    const reorderedClosableTabs = closableTabIndexes.map((index) => tabs.value[index]);
    const [movedTab] = reorderedClosableTabs.splice(from, 1);
    if (!movedTab) {
      return;
    }
    reorderedClosableTabs.splice(to, 0, movedTab);

    const nextTabs = [...tabs.value];
    closableTabIndexes.forEach((tabIndex, orderIndex) => {
      nextTabs[tabIndex] = reorderedClosableTabs[orderIndex];
    });

    tabs.value = nextTabs;
    persistTabs();
  }

  return {
    tabs,
    activeName,
    hydrateTabs,
    persistTabs,
    sanitizeTabs,
    reorderClosableTabs,
    ensureTab,
    removeTab,
    closeOthers,
    closeAll
  };
});
