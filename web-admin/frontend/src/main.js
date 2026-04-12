import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

import App from "./App.vue";
import router from "./router";
import { useAuthStore } from "./stores/auth";
import { useLocaleStore } from "./stores/locale";
import "./assets/design-tokens.css";
import "./assets/base.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

const authStore = useAuthStore(pinia);
authStore.restoreSession();

const localeStore = useLocaleStore(pinia);
localeStore.restoreLocale();

app.use(router);
app.use(ElementPlus);
app.mount("#app");
