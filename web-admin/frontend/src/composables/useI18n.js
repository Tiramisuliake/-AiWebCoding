import { computed } from "vue";

import messages from "../i18n/messages";
import { useLocaleStore } from "../stores/locale";

function getValueByPath(source, path) {
  return path.split(".").reduce((acc, key) => (acc ? acc[key] : undefined), source);
}

export function useI18n() {
  const localeStore = useLocaleStore();
  const fallbackLocale = "en-US";

  const dictionary = computed(
    () => messages[localeStore.locale] || messages[fallbackLocale]
  );

  function t(key, params = {}) {
    const template =
      getValueByPath(dictionary.value, key) ??
      getValueByPath(messages[fallbackLocale], key) ??
      key;

    return Object.entries(params).reduce((text, [name, value]) => {
      return text.replaceAll(`{${name}}`, String(value));
    }, template);
  }

  return {
    t,
    locale: computed(() => localeStore.locale),
    setLocale: localeStore.setLocale,
    supportedLocales: localeStore.supportedLocales
  };
}
