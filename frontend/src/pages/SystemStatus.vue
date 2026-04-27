<template>
  <div style="padding:12px;">
    <el-card>
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
        <div>
          <div style="font-weight:800;">系统状态</div>
          <div style="color:#666;font-size:12px;margin-top:6px;">
            用于答辩演示：快速确认数据库/缓存可用、聚合任务是否在更新。
          </div>
        </div>
        <div style="display:flex; gap:8px;">
          <el-button @click="load">刷新</el-button>
        </div>
      </div>
    </el-card>

    <div style="display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:12px; margin-top:12px;">
      <el-card>
        <div style="font-weight:700;margin-bottom:8px;">PostgreSQL</div>
        <el-tag :type="status.postgres.ok ? 'success' : 'danger'">
          {{ status.postgres.ok ? '正常' : '异常' }}
        </el-tag>
        <div v-if="!status.postgres.ok" style="margin-top:8px;color:#a00;">
          {{ status.postgres.error }}
        </div>
      </el-card>

      <el-card>
        <div style="font-weight:700;margin-bottom:8px;">Redis</div>
        <el-tag :type="status.redis.ok ? 'success' : 'danger'">
          {{ status.redis.ok ? '正常' : '异常' }}
        </el-tag>
        <div v-if="!status.redis.ok" style="margin-top:8px;color:#a00;">
          {{ status.redis.error }}
        </div>
      </el-card>
    </div>

    <el-card style="margin-top:12px;">
      <div style="font-weight:700;margin-bottom:8px;">定时聚合任务（间接指标）</div>
      <div style="color:#666;font-size:12px;margin-bottom:8px;">
        说明：Celery/Beat 运行状态更适合通过容器日志确认，此处用“最近一次聚合时间”作为间接判断。
      </div>
      <div v-if="status.last_aggregation">
        最近一次聚合：<b>{{ formatTime(status.last_aggregation.ts) }}</b>
        <div style="margin-top:6px;">
          <pre style="margin:0; background:#111;color:#ddd;padding:10px;overflow:auto;">{{ JSON.stringify(status.last_aggregation.detail, null, 2) }}</pre>
        </div>
      </div>
      <div v-else style="color:#888;">
        暂无聚合记录（请等待 30 秒，或检查 worker/beat 日志）。
      </div>
    </el-card>

    <div style="color:#888;font-size:12px;margin-top:10px;">
      状态生成时间：{{ formatTime(status.generated_at) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from "vue";
import { api, loadToken } from "../api/client";
import { useRouter } from "vue-router";
import { msgError, msgSuccess } from "../utils/notify";
import { formatTime } from "../utils/time";

const router = useRouter();

const status = reactive<any>({
  generated_at: "",
  postgres: { ok: false, error: "" },
  redis: { ok: false, error: "" },
  last_aggregation: null,
});

async function load() {
  loadToken();
  try {
    const resp = await api.get("/api/system/status");
    Object.assign(status, resp.data);
    msgSuccess("已刷新系统状态");
  } catch (e: any) {
    msgError("获取系统状态失败：" + (e?.response?.data?.detail || "未知错误"));
    router.push("/login");
  }
}

onMounted(load);
</script>