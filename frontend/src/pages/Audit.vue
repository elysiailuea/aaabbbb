<template>
  <div style="padding:12px;">
    <el-card>
      <div style="font-weight:800;margin-bottom:8px;">审计日志</div>
      <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
        <el-input v-model="actor" placeholder="操作者（精确）" style="width:200px;" />
        <el-input v-model="action" placeholder="动作包含（例如 ban / alert / settings / demo）" style="width:320px;" />
        <div style="display:flex; align-items:center; gap:6px;">
          <span style="color:#666;">条数</span>
          <el-input-number v-model="limit" :min="50" :max="1000" :step="50" />
        </div>
        <el-button type="primary" @click="load">查询</el-button>
      </div>
      <div style="color:#888;font-size:12px;margin-top:8px;">
        说明：关键操作（封禁/解封、告警确认/关闭、策略变更、演示数据生成/清理、定时聚合）都会记录到审计日志。
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <el-table :data="rows" style="width:100%;">
        <el-table-column label="时间" width="190">
          <template #default="{ row }">{{ formatTime(row.ts) }}</template>
        </el-table-column>
        <el-table-column prop="actor" label="操作者" width="140" />
        <el-table-column prop="action" label="动作" width="220" />
        <el-table-column label="详情">
          <template #default="{ row }">
            <pre style="margin:0;white-space:pre-wrap;">{{ JSON.stringify(row.detail) }}</pre>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api, loadToken } from "../api/client";
import { formatTime } from "../utils/time";

const router = useRouter();
const rows = ref<any[]>([]);
const actor = ref("");
const action = ref("");
const limit = ref(200);

async function load() {
  loadToken();
  const params: any = { limit: limit.value };
  if (actor.value) params.actor = actor.value;
  if (action.value) params.action = action.value;

  try {
    const resp = await api.get("/api/audit", { params });
    rows.value = action.value
      ? resp.data.filter((x: any) => String(x.action || "").includes(action.value))
      : resp.data;
  } catch {
    router.push("/login");
  }
}

onMounted(load);
</script>