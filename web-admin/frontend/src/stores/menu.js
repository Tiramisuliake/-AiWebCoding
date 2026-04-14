import { computed, ref } from "vue";
import { defineStore } from "pinia";

import { fetchMenuTree, fetchMyMenuTree } from "../api/rbac";

function walkTree(nodes, visitor) {
  for (const node of nodes || []) {
    visitor(node);
    if (node.children?.length) {
      walkTree(node.children, visitor);
    }
  }
}

export const useMenuStore = defineStore("menu", () => {
  const userMenuTree = ref([]);
  const manageMenuTree = ref([]);
  const loaded = ref(false);

  const allowedPaths = computed(() => {
    const pathSet = new Set(["/"]);
    walkTree(userMenuTree.value, (node) => {
      if (node.route_path) {
        pathSet.add(node.route_path);
      }
    });
    return pathSet;
  });

  async function loadMyMenus() {
    const response = await fetchMyMenuTree();
    if (response.code !== 0) {
      throw new Error(response.msg || "Load menu failed");
    }
    userMenuTree.value = response.data.items || [];
    loaded.value = true;
  }

  async function loadManageMenus() {
    const response = await fetchMenuTree();
    if (response.code !== 0) {
      throw new Error(response.msg || "Load manage menus failed");
    }
    manageMenuTree.value = response.data.items || [];
  }

  function reset() {
    userMenuTree.value = [];
    manageMenuTree.value = [];
    loaded.value = false;
  }

  function hasPath(path) {
    return allowedPaths.value.has(path);
  }

  return {
    userMenuTree,
    manageMenuTree,
    allowedPaths,
    loaded,
    loadMyMenus,
    loadManageMenus,
    hasPath,
    reset
  };
});

