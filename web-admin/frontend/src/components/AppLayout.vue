<script setup>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useI18n } from "../composables/useI18n";
import { useAuthStore } from "../stores/auth";
import { useTabsStore } from "../stores/tabs";

const authStore = useAuthStore();
const tabsStore = useTabsStore();
const route = useRoute();
const router = useRouter();
const menuOpen = ref(false);
const { t, locale, setLocale } = useI18n();

const navItems = computed(() => [
  { name: "dashboard", path: "/", label: t("common.dashboard") },
  { name: "users", path: "/users", label: t("common.users") },
  { name: "roles", path: "/roles", label: t("common.roles") },
  { name: "permissions", path: "/permissions", label: t("common.permissions") }
]);

const currentTitle = computed(() => {
  return route.meta?.titleKey ? t(route.meta.titleKey) : t("common.appName");
});

const displayName = computed(() => authStore.user?.username || t("common.unknown"));

const localeOptions = computed(() => [
  { value: "zh-CN", label: t("common.chinese") },
  { value: "en-US", label: t("common.english") }
]);

watch(
  () => route.fullPath,
  () => {
    tabsStore.ensureTab(route);
  },
  { immediate: true }
);

async function onLogout() {
  await authStore.logout();
  router.push({ name: "login" });
}

function isActive(path) {
  if (path === "/") {
    return route.path === "/";
  }
  return route.path.startsWith(path);
}

function navigate(path) {
  menuOpen.value = false;
  router.push(path);
}

function onLocaleChange(value) {
  setLocale(value);
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
  <div class="layout-shell">
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand">
        <span class="brand-mark">WA</span>
        <div class="brand-text">
          <span class="brand-name">{{ t("common.appName") }}</span>
          <span class="brand-subtitle">{{ t("layout.subtitle") }}</span>
        </div>
      </div>
      <nav class="nav-list">
        <button
          v-for="item in navItems"
          :key="item.name"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="navigate(item.path)"
        >
          <span class="nav-dot"></span>
          {{ item.label }}
        </button>
      </nav>
    </aside>

    <div class="layout-main">
      <header class="topbar">
        <div class="title-wrap">
          <button class="menu-toggle" @click="menuOpen = !menuOpen">
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
          <el-select
            :model-value="locale"
            size="small"
            style="width: 110px"
            @change="onLocaleChange"
          >
            <el-option
              v-for="option in localeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
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
}

.sidebar {
  background: linear-gradient(175deg, #0f172a 0%, #1e293b 72%);
  color: var(--color-aside-text);
  padding: var(--space-3) var(--space-2);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 5;
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
  display: none;
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
