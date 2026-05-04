import { ref } from "vue";
import { defineStore } from "pinia";

const LOCALE_KEY = "web_admin_locale";
const FIXED_LOCALE = "zh-CN";
const SUPPORTED_LOCALES = [FIXED_LOCALE];

export const useLocaleStore = defineStore("locale", () => {
  const locale = ref(FIXED_LOCALE);

  function restoreLocale() {
    locale.value = FIXED_LOCALE;
    localStorage.setItem(LOCALE_KEY, FIXED_LOCALE);
  }

  function setLocale(nextLocale) {
    if (nextLocale !== FIXED_LOCALE) {
      return;
    }
    locale.value = FIXED_LOCALE;
    localStorage.setItem(LOCALE_KEY, FIXED_LOCALE);
  }

  return {
    locale,
    supportedLocales: SUPPORTED_LOCALES,
    restoreLocale,
    setLocale
  };
});
