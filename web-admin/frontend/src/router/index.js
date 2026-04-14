import { createRouter, createWebHistory } from "vue-router";

import AppLayout from "../components/AppLayout.vue";
import DashboardView from "../views/DashboardView.vue";
import LoginView from "../views/LoginView.vue";
import MenuManageView from "../views/MenuManageView.vue";
import PermissionsView from "../views/PermissionsView.vue";
import RolesView from "../views/RolesView.vue";
import UsersView from "../views/UsersView.vue";
import { useAuthStore } from "../stores/auth";
import { useMenuStore } from "../stores/menu";

const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: {
      tab: false,
      keepAlive: false,
      titleKey: "login.title"
    }
  },
  {
    path: "/",
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "dashboard",
        component: DashboardView,
        meta: {
          titleKey: "common.dashboard",
          keepAlive: true,
          tab: true
        }
      },
      {
        path: "users",
        name: "users",
        component: UsersView,
        meta: {
          titleKey: "common.users",
          keepAlive: true,
          tab: true
        }
      },
      {
        path: "roles",
        name: "roles",
        component: RolesView,
        meta: {
          titleKey: "common.roles",
          keepAlive: true,
          tab: true
        }
      },
      {
        path: "permissions",
        name: "permissions",
        component: PermissionsView,
        meta: {
          titleKey: "common.permissions",
          keepAlive: true,
          tab: true
        }
      },
      {
        path: "menus",
        name: "menus",
        component: MenuManageView,
        meta: {
          titleKey: "common.menus",
          keepAlive: true,
          tab: true
        }
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  const menuStore = useMenuStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && authStore.isAuthenticated) {
    return { name: "dashboard" };
  }

  if (to.meta.requiresAuth && authStore.isAuthenticated && !menuStore.loaded) {
    try {
      await menuStore.loadMyMenus();
    } catch (_error) {
      authStore.clearSession();
      return { name: "login", query: { redirect: to.fullPath } };
    }
  }

  if (to.meta.requiresAuth && to.path !== "/" && !menuStore.hasPath(to.path)) {
    const firstAllowed = [...menuStore.allowedPaths][0] || "/";
    return firstAllowed === to.path ? true : firstAllowed;
  }

  return true;
});

export default router;
