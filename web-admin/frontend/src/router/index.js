import { createRouter, createWebHistory } from "vue-router";

import AppLayout from "../components/AppLayout.vue";
import DashboardView from "../views/DashboardView.vue";
import LoginView from "../views/LoginView.vue";
import PermissionsView from "../views/PermissionsView.vue";
import RolesView from "../views/RolesView.vue";
import UsersView from "../views/UsersView.vue";
import { useAuthStore } from "../stores/auth";

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
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && authStore.isAuthenticated) {
    return { name: "dashboard" };
  }
  return true;
});

export default router;
