<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useI18n } from "../composables/useI18n";
import { useAuthStore } from "../stores/auth";
import { useMenuStore } from "../stores/menu";
import { useTabsStore } from "../stores/tabs";

const authStore = useAuthStore();
const menuStore = useMenuStore();
const tabsStore = useTabsStore();
const route = useRoute();
const router = useRouter();
const menuOpen = ref(false);
const sidebarCollapsed = ref(false);
const expandedGroupKeys = ref([]);
const { t } = useI18n();
const SIDEBAR_COLLAPSED_KEY = "web_admin_sidebar_collapsed";

const navItems = computed(() => menuStore.userMenuTree || []);
const menuTitleKeyMap = Object.freeze({
  "/": "common.dashboard",
  "/users": "common.users",
  "/roles": "common.roles",
  "/permissions": "common.permissions",
  "/menus": "common.menus"
});

const currentTitle = computed(() => {
  return route.meta?.titleKey ? t(route.meta.titleKey) : t("common.appName");
});

const displayName = computed(() => authStore.user?.username || t("common.unknown"));

watch(
  () => route.fullPath,
  () => {
    tabsStore.ensureTab(route);
    syncExpandedGroupsWithRoute();
    if (window.innerWidth <= 900) {
      menuOpen.value = false;
    }
  },
  { immediate: true }
);

watch(
  navItems,
  () => {
    syncExpandedGroupsWithRoute();
  },
  { deep: true }
);

onMounted(() => {
  const stored = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
  sidebarCollapsed.value = stored === "1";
});

async function onLogout() {
  await authStore.logout();
  router.push({ name: "login" });
}

function isActive(path) {
  return isPathActive(path, route.path);
}

function isPathActive(path, currentPath) {
  if (!path) {
    return false;
  }
  if (path === "/") {
    return currentPath === "/";
  }
  return currentPath.startsWith(path);
}

function getMenuKey(item) {
  return String(item?.id ?? item?.route_path ?? item?.name ?? "");
}

function hasActiveDescendant(nodes, currentPath) {
  for (const node of nodes || []) {
    if (isPathActive(node.route_path, currentPath)) {
      return true;
    }
    if (node.children?.length && hasActiveDescendant(node.children, currentPath)) {
      return true;
    }
  }
  return false;
}

function isGroupExpanded(item) {
  return expandedGroupKeys.value.includes(getMenuKey(item));
}

function isGroupActive(item) {
  return isPathActive(item?.route_path, route.path) || hasActiveDescendant(item?.children, route.path);
}

function findAncestorKeysByPath(nodes, currentPath, ancestors = []) {
  for (const node of nodes || []) {
    if (!node.children?.length) {
      continue;
    }
    const key = getMenuKey(node);
    const nextAncestors = key ? [...ancestors, key] : ancestors;

    if (hasActiveDescendant(node.children, currentPath)) {
      const nested = findAncestorKeysByPath(node.children, currentPath, nextAncestors);
      return nested.length ? nested : nextAncestors;
    }

    const nested = findAncestorKeysByPath(node.children, currentPath, nextAncestors);
    if (nested.length) {
      return nested;
    }
  }
  return [];
}

function syncExpandedGroupsWithRoute() {
  const ancestors = findAncestorKeysByPath(navItems.value, route.path);
  if (!ancestors.length) {
    return;
  }
  const next = new Set(expandedGroupKeys.value);
  for (const key of ancestors) {
    next.add(key);
  }
  expandedGroupKeys.value = [...next];
}

function onGroupToggle(item) {
  const key = getMenuKey(item);
  if (!key) {
    return;
  }
  const next = new Set(expandedGroupKeys.value);
  if (next.has(key)) {
    next.delete(key);
  } else {
    next.add(key);
  }
  expandedGroupKeys.value = [...next];
}

function navigate(path) {
  if (!path) {
    return;
  }
  if (window.innerWidth <= 900) {
    menuOpen.value = false;
  }
  router.push(path);
}

function onSidebarToggle() {
  if (window.innerWidth <= 900) {
    menuOpen.value = !menuOpen.value;
    return;
  }
  sidebarCollapsed.value = !sidebarCollapsed.value;
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, sidebarCollapsed.value ? "1" : "0");
}

function resolveMenuTitle(item) {
  const titleKey = menuTitleKeyMap[item?.route_path];
  if (titleKey) {
    return t(titleKey);
  }
  return item?.name || "";
}

function onTabClick(tabPane) {
  const name = String(tabPane.paneName ?? tabPane.props.name);
  const target = tabsStore.tabs.find((item) => item.name === name);
  if (target) {
    router.push(target.path);
  }
}

function onTabRemove(name) {
  const nextPath = tabsStore.removeTab(String(name));
  router.push(nextPath);
}

function onTabCommand(command) {
  const currentName = String(route.name || "dashboard");
  if (command === "closeCurrent") {
    const nextPath = tabsStore.removeTab(currentName);
    router.push(nextPath);
    return;
  }
  if (command === "closeOthers") {
    const nextPath = tabsStore.closeOthers(currentName);
    router.push(nextPath);
    return;
  }
  if (command === "closeAll") {
    const nextPath = tabsStore.closeAll();
    router.push(nextPath);
  }
}
</script>

<template>
  <div class="layout-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <aside class="sidebar" :class="{ open: menuOpen, collapsed: sidebarCollapsed }">
      <div class="brand">
        <span class="brand-mark">WA</span>
        <div class="brand-text">
          <span class="brand-name">{{ t("common.appName") }}</span>
          <span class="brand-subtitle">{{ t("layout.subtitle") }}</span>
        </div>
      </div>
      <nav class="nav-list">
        <template v-for="item in navItems" :key="item.id">
          <button
            v-if="!item.children?.length"
            class="nav-item"
            :class="{ active: isActive(item.route_path) }"
            @click="navigate(item.route_path)"
          >
            <span class="nav-dot"></span>
            <span class="nav-label">{{ resolveMenuTitle(item) }}</span>
          </button>

          <section v-else class="nav-group">
            <button
              class="nav-item nav-parent"
              :class="{ active: isGroupActive(item), expanded: isGroupExpanded(item) }"
              @click="onGroupToggle(item)"
            >
              <span class="nav-dot"></span>
              <span class="nav-label">{{ resolveMenuTitle(item) }}</span>
              <span class="nav-caret" :class="{ expanded: isGroupExpanded(item) }"></span>
            </button>
            <div v-show="isGroupExpanded(item)" class="nav-children">
              <button
                v-for="child in item.children"
                :key="child.id"
                class="nav-item nav-child"
                :class="{ active: isActive(child.route_path) }"
                @click="navigate(child.route_path)"
              >
                <span class="nav-dot"></span>
                <span class="nav-label">{{ resolveMenuTitle(child) }}</span>
              </button>
            </div>
          </section>
        </template>
      </nav>
    </aside>

    <div class="layout-main">
      <header class="topbar">
        <div class="title-wrap">
          <button class="menu-toggle" @click="onSidebarToggle">
            <span></span>
            <span></span>
            <span></span>
          </button>
          <div>
            <h1 class="page-title">{{ currentTitle }}</h1>
            <p class="page-subtitle">{{ t("layout.welcome", { name: displayName }) }}</p>
          </div>
        </div>

        <div class="topbar-right">
          <el-button type="danger" plain @click="onLogout">{{ t("common.logout") }}</el-button>
        </div>
      </header>

      <section class="tabbar">
        <div class="tab-scroll">
          <el-tabs
            v-model="tabsStore.activeName"
            type="card"
            class="tabs"
            @tab-click="onTabClick"
            @tab-remove="onTabRemove"
          >
            <el-tab-pane
              v-for="tab in tabsStore.tabs"
              :key="tab.name"
              :label="t(tab.titleKey)"
              :name="tab.name"
              :closable="tab.closable"
            />
          </el-tabs>
        </div>

        <div class="tab-tools">
          <el-dropdown @command="onTabCommand">
            <el-button size="small" text>{{ t("tabs.actions") }}</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="closeCurrent">{{ t("tabs.closeCurrent") }}</el-dropdown-item>
                <el-dropdown-item command="closeOthers">{{ t("tabs.closeOthers") }}</el-dropdown-item>
                <el-dropdown-item command="closeAll">{{ t("tabs.closeAll") }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </section>

      <main class="content" @click="menuOpen = false">
        <div class="content-shell">
          <RouterView v-slot="{ Component, route: currentRoute }">
            <KeepAlive>
              <component
                :is="Component"
                v-if="currentRoute.meta.keepAlive"
                :key="currentRoute.name"
              />
            </KeepAlive>
            <component
              :is="Component"
              v-if="!currentRoute.meta.keepAlive"
              :key="currentRoute.fullPath"
            />
          </RouterView>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: var(--aside-width) 1fr;
  background: linear-gradient(155deg, #f8fafc 0%, #eef2ff 100%);
  transition: grid-template-columns 0.2s ease;
}

.layout-shell.sidebar-collapsed {
  grid-template-columns: 78px 1fr;
}

.sidebar {
  background: linear-gradient(175deg, #0f172a 0%, #1e293b 72%);
  color: var(--color-aside-text);
  padding: var(--space-3) var(--space-2);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 5;
  overflow: hidden;
  transition: padding 0.2s ease, transform 0.2s ease;
}

.sidebar.collapsed {
  padding-left: 10px;
  padding-right: 10px;
}

.sidebar.collapsed .brand {
  justify-content: center;
}

.sidebar.collapsed .brand-text {
  display: none;
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  margin-bottom: var(--space-4);
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-base);
  display: grid;
  place-items: center;
  background: linear-gradient(145deg, #2563eb, #1d4ed8);
  font-weight: var(--font-weight-semibold);
  color: #fff;
}

.brand-text {
  display: grid;
}

.brand-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: #fff;
}

.brand-subtitle {
  font-size: var(--font-size-xs);
  color: rgba(203, 213, 225, 0.8);
}

.nav-list {
  display: grid;
  gap: 6px;
}

.nav-group {
  display: grid;
  gap: 4px;
}

.nav-children {
  display: grid;
  gap: 4px;
}

.nav-item {
  width: 100%;
  text-align: left;
  border: 0;
  color: inherit;
  background: transparent;
  padding: 11px 12px;
  border-left: var(--accent-border-width) solid transparent;
  border-radius: 0 var(--radius-base) var(--radius-base) 0;
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-label {
  white-space: nowrap;
}

.nav-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.35);
}

.nav-item:hover {
  background: rgba(59, 130, 246, 0.22);
}

.nav-item.active {
  border-left-color: var(--color-accent);
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.38), rgba(37, 99, 235, 0.2));
  color: #fff;
}

.nav-item.active .nav-dot {
  background: #fff;
}

.nav-parent {
  font-weight: 600;
}

.nav-parent .nav-label {
  flex: 1;
}

.nav-caret {
  width: 8px;
  height: 8px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(45deg);
  transition: transform 0.2s ease;
  opacity: 0.75;
}

.nav-caret.expanded {
  transform: rotate(225deg);
}

.nav-child {
  margin-left: 14px;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding-left: 8px;
  padding-right: 8px;
}

.sidebar.collapsed .nav-label {
  display: none;
}

.sidebar.collapsed .nav-child {
  margin-left: 0;
}

.sidebar.collapsed .nav-caret,
.sidebar.collapsed .nav-children {
  display: none;
}

.layout-main {
  min-width: 0;
  display: grid;
  grid-template-rows: var(--header-height) 52px 1fr;
}

.topbar {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-3);
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.page-title {
  margin: 0;
  font-size: 18px;
  line-height: 1.1;
}

.page-subtitle {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.menu-toggle {
  width: 34px;
  height: 34px;
  border: 0;
  background: rgba(148, 163, 184, 0.18);
  border-radius: var(--radius-base);
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 3px;
  flex-direction: column;
  cursor: pointer;
}

.menu-toggle span {
  display: block;
  width: 15px;
  height: 2px;
  background: #0f172a;
  border-radius: 99px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.tabbar {
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: var(--space-2);
  padding: 0 var(--space-3);
}

.tab-scroll {
  min-width: 0;
}

.tab-tools {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border-left: 1px solid rgba(148, 163, 184, 0.28);
  padding-left: var(--space-2);
}

.tabs {
  min-width: 0;
}

.tabs :deep(.el-tabs__header) {
  margin: 0;
  border-bottom: 0;
}

.tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.tabs :deep(.el-tabs__item) {
  height: 34px;
  line-height: 34px;
}

.content {
  overflow: auto;
  padding: var(--space-2);
}

.content-shell {
  width: 100%;
  max-width: 1480px;
  margin: 0 auto;
}

@media (max-width: 900px) {
  .layout-shell {
    grid-template-columns: 1fr;
  }

  .layout-shell.sidebar-collapsed {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    width: min(75vw, 280px);
    transform: translateX(-100%);
    transition: transform 0.2s ease;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .menu-toggle {
    display: inline-flex;
  }

  .topbar,
  .tabbar,
  .content {
    padding-left: var(--space-2);
    padding-right: var(--space-2);
  }
}
</style>
