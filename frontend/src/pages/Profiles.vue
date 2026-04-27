<template>
  <div style="padding:12px;">
    <el-card>
      <div style="display:flex; gap:8px; align-items:center;">
        <el-button @click="load">刷新</el-button>
        <span style="color:#666;font-size:12px;">
          说明：画像由 Celery 定时聚合（默认 30 秒），包含 1 小时窗口统计、指纹、风险评分。
        </span>
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <el-table :data="rows" style="width:100%">
        <el-table-column label="最近出现" width="190">
          <template #default="{ row }">{{ formatTime(row.last_seen) }}</template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" width="120"/>
        <el-table-column prop="risk_score" label="评分" width="90"/>
        <el-table-column prop="src_ip" label="IP" width="160"/>
        <el-table-column prop="peak_rpm_1h" label="峰值RPM" width="110"/>
        <el-table-column prop="http_count_1h" label="HTTP(1h)" width="110"/>
        <el-table-column prop="ssh_fail_count_1h" label="SSH失败(1h)" width="130"/>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="detail(row.src_ip)">详情</el-button>
            <el-button size="small" type="danger" plain @click="ban(row.src_ip)" :disabled="row.risk_level==='low'">封禁</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, loadToken } from "../api/client";
import { useRouter } from "vue-router";
import { msgError } from "../utils/notify";
import { formatTime } from "../utils/time";

const router = useRouter();
const rows = ref<any[]>([]);

function detail(ip: string) {
  router.push(`/app/profiles/${encodeURIComponent(ip)}`);
}

async function load() {
  loadToken();
  try {
    const resp = await api.get("/api/profiles");
    rows.value = resp.data;
  } catch {
    router.push("/login");
  }
}

async function ban(ip: string) {
  loadToken();
  try {
    await api.post("/api/bans", { src_ip: ip, reason: "manual:from_profile", level: "high", ttl_seconds: 3600, evidence: {} });
    router.push("/app/bans");
  } catch (e: any) {
    msgError("操作失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

onMounted(load);
</script>