import { computed, ref } from "vue";
import { defineStore } from "pinia";

import * as authApi from "../api/auth";
import { useMenuStore } from "./menu";

const ACCESS_KEY = "web_admin_access_token";
const REFRESH_KEY = "web_admin_refresh_token";
const USER_KEY = "web_admin_user";

export const useAuthStore = defineStore("auth", () => {
  const menuStore = useMenuStore();
  const accessToken = ref("");
  const refreshTokenValue = ref("");
  const user = ref(null);
  const loading = ref(false);

  const isAuthenticated = computed(() => Boolean(accessToken.value));

  function persist() {
    if (accessToken.value) {
      localStorage.setItem(ACCESS_KEY, accessToken.value);
    } else {
      localStorage.removeItem(ACCESS_KEY);
    }

    if (refreshTokenValue.value) {
      localStorage.setItem(REFRESH_KEY, refreshTokenValue.value);
    } else {
      localStorage.removeItem(REFRESH_KEY);
    }

    if (user.value) {
      localStorage.setItem(USER_KEY, JSON.stringify(user.value));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  }

  function restoreSession() {
    accessToken.value = localStorage.getItem(ACCESS_KEY) || "";
    refreshTokenValue.value = localStorage.getItem(REFRESH_KEY) || "";
    const rawUser = localStorage.getItem(USER_KEY);
    user.value = rawUser ? JSON.parse(rawUser) : null;
  }

  function clearSession() {
    accessToken.value = "";
    refreshTokenValue.value = "";
    user.value = null;
    menuStore.reset();
    persist();
  }

  async function login(credentials) {
    loading.value = true;
    try {
      const response = await authApi.login(credentials);
      if (response.code !== 0) {
        throw new Error(response.msg || "Login failed");
      }

      accessToken.value = response.data.access_token;
      refreshTokenValue.value = response.data.refresh_token;
      user.value = response.data.user;
      persist();
      await menuStore.loadMyMenus();
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      if (accessToken.value) {
        await authApi.logout();
      }
    } catch (_error) {
      // Best-effort logout; local state still gets cleared.
    } finally {
      clearSession();
    }
  }

  return {
    accessToken,
    refreshTokenValue,
    user,
    loading,
    isAuthenticated,
    restoreSession,
    clearSession,
    login,
    logout
  };
});
