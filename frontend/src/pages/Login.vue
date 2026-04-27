<template>
  <div style="max-width: 420px; margin: 80px auto; background:#fff; padding:18px; border:1px solid #eee;">
    <h2 style="margin-top:0;">登录</h2>
    <el-form @submit.prevent>
      <el-form-item label="用户名">
        <el-input v-model="username" autocomplete="username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="password" type="password" autocomplete="current-password" />
      </el-form-item>
      <div style="display:flex; gap:8px;">
        <el-button type="primary" @click="doLogin">登录</el-button>
        <el-button @click="fillAdmin">管理员</el-button>
        <el-button @click="fillOperator">安全员</el-button>
        <el-button @click="fillViewer">只读</el-button>
      </div>
    </el-form>

    <el-divider />

    <div style="color:#666; font-size:13px; line-height:1.6;">
      <div><b>演示账号：</b></div>
      <div>管理员：admin / admin123（可修改策略、封禁/解封、演示模式）</div>
      <div>安全员：operator / operator123（可确认告警、封禁/解封）</div>
      <div>只读：viewer / viewer123（仅查看）</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { api, setToken } from "../api/client";
import { useRouter } from "vue-router";
import { msgError, msgSuccess } from "../utils/notify";

const router = useRouter();
const username = ref("admin");
const password = ref("admin123");

function fillAdmin() { username.value = "admin"; password.value = "admin123"; }
function fillOperator() { username.value = "operator"; password.value = "operator123"; }
function fillViewer() { username.value = "viewer"; password.value = "viewer123"; }

async function doLogin() {
  try {
    const resp = await api.post("/api/auth/login", { username: username.value, password: password.value });
    setToken(resp.data.access_token);

    const me = await api.get("/api/auth/me");
    localStorage.setItem("me.username", me.data.username);
    localStorage.setItem("me.role", me.data.role);

    msgSuccess("登录成功");
    router.push("/app/dashboard");
  } catch (e: any) {
    msgError("登录失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}
</script>