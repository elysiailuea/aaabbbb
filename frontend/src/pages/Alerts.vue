<template>
  <div style="padding:12px;">
    <el-card>
      <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <el-button @click="load">刷新</el-button>
        <span style="color:#666;font-size:12px;">
          提示：告警使用时间窗去重（同 IP + 指纹 + 类型，在窗口内只更新命中次数与窗口结束时间）。
        </span>
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <el-table :data="alerts" style="width:100%" @row-click="openDetail">
        <el-table-column label="时间" width="190">
          <template #default="{ row }">{{ formatTime(row.window_end) }}</template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="120"/>
        <el-table-column prop="src_ip" label="来源 IP" width="160"/>
        <el-table-column prop="title" label="标题"/>
        <el-table-column prop="hit_count" label="命中次数" width="100"/>
        <el-table-column prop="status" label="状态" width="110"/>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" @click.stop="ack(row.id)" :disabled="row.status==='closed'">确认</el-button>
            <el-button size="small" @click.stop="close(row.id)" :disabled="row.status==='closed'">关闭</el-button>
            <el-button size="small" type="primary" plain @click.stop="goProfile(row.src_ip)">画像</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="color:#888;font-size:12px;margin-top:8px;">
        提示：点击任意一行可打开“告警详情”抽屉查看 evidence（证据字段）。
      </div>
    </el-card>

    <el-drawer v-model="drawerOpen" title="告警详情" size="45%">
      <div v-if="selected" style="display:flex; flex-direction:column; gap:10px;">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="告警 ID">{{ selected.id }}</el-descriptions-item>
          <el-descriptions-item label="来源 IP">{{ selected.src_ip }}</el-descriptions-item>
          <el-descriptions-item label="级别">{{ selected.level }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ selected.alert_type }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ selected.status }}</el-descriptions-item>
          <el-descriptions-item label="命中次数">{{ selected.hit_count }}</el-descriptions-item>
          <el-descriptions-item label="窗口开始">{{ formatTime(selected.window_start) }}</el-descriptions-item>
          <el-descriptions-item label="窗口结束">{{ formatTime(selected.window_end) }}</el-descriptions-item>
          <el-descriptions-item label="指纹">{{ selected.fingerprint }}</el-descriptions-item>
        </el-descriptions>

        <el-card v-if="selected?.evidence?.risk_reasons?.length">
          <div style="font-weight:700;margin-bottom:6px;">评分构成 / 命中规则</div>
          <el-tag
            v-for="(r, idx) in selected.evidence.risk_reasons"
            :key="idx"
            style="margin:4px 6px 0 0;"
            type="warning"
          >
            {{ r }}
          </el-tag>
        </el-card>

        <el-card>
          <div style="font-weight:700;margin-bottom:6px;">证据（evidence）</div>
          <pre style="margin:0; background:#111;color:#ddd;padding:12px;overflow:auto;">{{ JSON.stringify(selected.evidence, null, 2) }}</pre>
        </el-card>

        <div style="display:flex; gap:8px;">
          <el-button type="primary" @click="goProfile(selected.src_ip)">查看画像</el-button>
          <el-button @click="goEvents(selected.src_ip)">查看该 IP 事件</el-button>
          <el-button type="warning" @click="ack(selected.id)" :disabled="selected.status==='closed'">确认告警</el-button>
          <el-button type="danger" @click="close(selected.id)" :disabled="selected.status==='closed'">关闭告警</el-button>
        </div>

        <div style="color:#888;font-size:12px;">
          权限说明：管理员/安全员可确认/关闭；只读用户仅可查看。
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, loadToken } from "../api/client";
import { useRouter } from "vue-router";
import { msgError, msgSuccess } from "../utils/notify";
import { formatTime } from "../utils/time";

const router = useRouter();
const alerts = ref<any[]>([]);

const drawerOpen = ref(false);
const selected = ref<any>(null);

function goProfile(ip: string) {
  router.push(`/app/profiles/${encodeURIComponent(ip)}`);
}

function goEvents(ip: string) {
  router.push({ path: "/app/events", query: { src_ip: ip, limit: "200" } });
}

function openDetail(row: any) {
  selected.value = row;
  drawerOpen.value = true;
}

async function load() {
  loadToken();
  try {
    const resp = await api.get("/api/alerts");
    alerts.value = resp.data;
  } catch {
    router.push("/login");
  }
}

async function ack(id: string) {
  loadToken();
  try {
    await api.post(`/api/alerts/${id}/ack`);
    msgSuccess("已确认告警");
    await load();
  } catch (e: any) {
    msgError("操作失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

async function close(id: string) {
  loadToken();
  try {
    await api.post(`/api/alerts/${id}/close`);
    msgSuccess("已关闭告警");
    await load();
  } catch (e: any) {
    msgError("操作失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

onMounted(load);
</script>