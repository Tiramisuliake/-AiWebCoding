import { ref } from "vue";
import { defineStore } from "pinia";

const LOCALE_KEY = "web_admin_locale";
const SUPPORTED_LOCALES = ["zh-CN", "en-US"];

export const useLocaleStore = defineStore("locale", () => {
  const locale = ref("zh-CN");

  function restoreLocale() {
    const stored = localStorage.getItem(LOCALE_KEY);
    if (stored && SUPPORTED_LOCALES.includes(stored)) {
      locale.value = stored;
    } else {
      locale.value = "zh-CN";
    }
  }

  function setLocale(nextLocale) {
    if (!SUPPORTED_LOCALES.includes(nextLocale)) {
      return;
    }
    locale.value = nextLocale;
    localStorage.setItem(LOCALE_KEY, nextLocale);
  }

  return {
    locale,
    supportedLocales: SUPPORTED_LOCALES,
    restoreLocale,
    setLocale
  };
});
