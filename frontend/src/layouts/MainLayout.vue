<template>
  <el-container style="height: 100vh;">
    <el-aside width="220px" style="border-right: 1px solid #eee;">
      <div style="padding:16px; font-weight:800; font-size:16px;">
        蜜罐联动防护平台
      </div>
      <el-menu :default-active="activePath" @select="onSelect" router>
        <el-menu-item index="/app/dashboard">总览看板</el-menu-item>
        <el-menu-item index="/app/alerts">告警中心</el-menu-item>
        <el-menu-item index="/app/profiles">攻击画像</el-menu-item>
        <el-menu-item index="/app/events">事件查询</el-menu-item>
        <el-menu-item index="/app/bans">封禁管理</el-menu-item>
        <el-menu-item index="/app/audit">审计日志</el-menu-item>
        <el-menu-item index="/app/settings">策略配置</el-menu-item>
        <el-menu-item index="/app/rules">规则说明</el-menu-item>
        <el-menu-item index="/app/system">系统状态</el-menu-item>
        <el-menu-item index="/app/demo">演示模式</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #eee;">
        <div style="font-weight:700;">
          {{ pageTitle }}
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
          <el-tag v-if="me.username" type="info">用户：{{ me.username }}</el-tag>
          <el-tag v-if="me.role" type="success">角色：{{ roleText(me.role) }}</el-tag>
          <el-button type="danger" plain size="small" @click="logout">退出登录</el-button>
        </div>
      </el-header>

      <el-main style="background:#fafafa;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, loadToken } from "../api/client";
import { msgError } from "../utils/notify";

const router = useRouter();
const route = useRoute();

const me = reactive<{ username: string; role: string }>({ username: "", role: "" });

const activePath = computed(() => route.path);

const pageTitle = computed(() => {
  const m: Record<string, string> = {
    "/app/dashboard": "总览看板",
    "/app/alerts": "告警中心",
    "/app/profiles": "攻击画像",
    "/app/events": "事件查询",
    "/app/bans": "封禁管理",
    "/app/audit": "审计日志",
    "/app/settings": "策略配置",
    "/app/rules": "规则说明",
    "/app/system": "系统状态",
    "/app/demo": "演示模式",
  };
  if (route.path.startsWith("/app/profiles/")) return "攻击画像详情";
  return m[route.path] || "控制台";
});

function onSelect(path: string) {
  router.push(path);
}

function roleText(role: string) {
  if (role === "admin") return "管理员";
  if (role === "operator") return "安全员";
  if (role === "viewer") return "只读访客";
  return role;
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("me.username");
  localStorage.removeItem("me.role");
  delete api.defaults.headers.common["Authorization"];
  router.push("/login");
}

async function loadMe() {
  loadToken();
  try {
    const resp = await api.get("/api/auth/me");
    me.username = resp.data.username;
    me.role = resp.data.role;
    localStorage.setItem("me.username", me.username);
    localStorage.setItem("me.role", me.role);
  } catch (e: any) {
    msgError("会话已失效，请重新登录");
    logout();
  }
}

onMounted(loadMe);
</script>