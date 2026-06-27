import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { setupRouterGuards } from "./router/guards";
import { useAuthStore } from "./stores/auth";
import "./assets/styles/main.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
setupRouterGuards(router);

const authStore = useAuthStore(pinia);
authStore.initialize().finally(() => {
  app.mount("#app");
});
