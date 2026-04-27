import { createRouter, createWebHistory } from "vue-router";
import Login from "./pages/Login.vue";
import MainLayout from "./layouts/MainLayout.vue";

import Dashboard from "./pages/Dashboard.vue";
import Alerts from "./pages/Alerts.vue";
import Profiles from "./pages/Profiles.vue";
import ProfileDetail from "./pages/ProfileDetail.vue";
import Events from "./pages/Events.vue";
import Bans from "./pages/Bans.vue";
import Audit from "./pages/Audit.vue";
import Settings from "./pages/Settings.vue";
import Rules from "./pages/Rules.vue";
import SystemStatus from "./pages/SystemStatus.vue";
import Demo from "./pages/Demo.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/app/dashboard" },
    { path: "/login", component: Login },
    {
      path: "/app",
      component: MainLayout,
      children: [
        { path: "dashboard", component: Dashboard },
        { path: "alerts", component: Alerts },
        { path: "profiles", component: Profiles },
        { path: "profiles/:ip", component: ProfileDetail },
        { path: "events", component: Events },
        { path: "bans", component: Bans },
        { path: "audit", component: Audit },
        { path: "settings", component: Settings },
        { path: "rules", component: Rules },
        { path: "system", component: SystemStatus },
        { path: "demo", component: Demo },
      ],
    },
  ],
});

router.beforeEach((to) => {
  if (to.path.startsWith("/app")) {
    const token = localStorage.getItem("token");
    if (!token) return "/login";
  }
  return true;
});

export default router;