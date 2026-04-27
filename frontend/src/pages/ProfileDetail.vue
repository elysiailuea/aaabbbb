<template>
  <div style="padding:12px;">
    <el-card>
      <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;">
        <div>
          <div style="font-weight:800;">攻击画像详情：{{ ip }}</div>
          <div style="color:#666;font-size:12px;">可导出 JSON/HTML 报告用于取证/论文附录。</div>
        </div>
        <div style="display:flex; gap:8px;">
          <el-button @click="load">刷新</el-button>
          <el-button type="danger" plain @click="ban">封禁</el-button>
          <el-button type="success" plain @click="exportReport">导出报告(JSON)</el-button>
          <el-button type="success" plain @click="exportReportHtml">导出报告(HTML)</el-button>
          <el-button type="primary" plain @click="back">返回</el-button>
        </div>
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <pre style="margin:0; background:#111;color:#ddd;padding:12px;overflow:auto;">{{ JSON.stringify(profile, null, 2) }}</pre>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, loadToken } from "../api/client";
import { msgError, msgSuccess } from "../utils/notify";

const route = useRoute();
const router = useRouter();
const ip = computed(() => String(route.params.ip || ""));
const profile = ref<any>({});

function back() { router.push("/app/profiles"); }

async function load() {
  loadToken();
  const resp = await api.get(`/api/profiles/${encodeURIComponent(ip.value)}`);
  profile.value = resp.data;
}

async function ban() {
  loadToken();
  try {
    await api.post("/api/bans", { src_ip: ip.value, reason: "manual:from_detail", level: "high", ttl_seconds: 3600, evidence: { from: "profile_detail" } });
    router.push("/app/bans");
  } catch (e: any) {
    msgError("操作失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

async function exportReport() {
  loadToken();
  const resp = await api.get(`/api/report/ip/${encodeURIComponent(ip.value)}`, { params: { hours: 24 } });
  const blob = new Blob([JSON.stringify(resp.data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `报告-${ip.value}.json`;
  a.click();
  URL.revokeObjectURL(url);
  msgSuccess("JSON 报告已开始下载");
}

async function exportReportHtml() {
  loadToken();
  try {
    const resp = await api.get(`/api/report/ip/${encodeURIComponent(ip.value)}/html`, { params: { hours: 24 }, responseType: "blob" });
    const blob = new Blob([resp.data], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `报告-${ip.value}.html`;
    a.click();
    URL.revokeObjectURL(url);
    msgSuccess("HTML 报告已开始下载");
  } catch (e: any) {
    msgError("导出失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

onMounted(load);
</script>