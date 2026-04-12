import { ref } from "vue";
import { defineStore } from "pinia";

const HOME_TAB = {
  name: "dashboard",
  path: "/",
  titleKey: "common.dashboard",
  closable: false
};

export const useTabsStore = defineStore("tabs", () => {
  const tabs = ref([{ ...HOME_TAB }]);
  const activeName = ref(HOME_TAB.name);

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
      return tabs.value.find((item) => item.name === activeName.value)?.path || HOME_TAB.path;
    }

    const fallback = tabs.value[targetIndex - 1] || tabs.value[targetIndex] || tabs.value[0];
    activeName.value = fallback?.name || HOME_TAB.name;
    return fallback?.path || HOME_TAB.path;
  }

  function closeOthers(name) {
    const keep = tabs.value.find((item) => item.name === name) || HOME_TAB;
    tabs.value = [tabs.value.find((item) => item.name === HOME_TAB.name) || HOME_TAB];
    if (keep.name !== HOME_TAB.name) {
      tabs.value.push(keep);
    }
    activeName.value = keep.name;
    return keep.path;
  }

  function closeAll() {
    tabs.value = [{ ...HOME_TAB }];
    activeName.value = HOME_TAB.name;
    return HOME_TAB.path;
  }

  return {
    tabs,
    activeName,
    ensureTab,
    removeTab,
    closeOthers,
    closeAll
  };
});
