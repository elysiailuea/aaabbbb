<template>
  <div style="padding:12px;">
    <el-card>
      <div style="font-weight:800;margin-bottom:8px;">事件查询（SOC 视图）</div>

      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
        <el-button size="small" @click="quickAll">全部</el-button>
        <el-button size="small" type="primary" plain @click="quickSensitive">敏感路径扫描</el-button>
        <el-button size="small" type="success" plain @click="quickSshBruteforce">SSH 爆破（失败登录）</el-button>
        <el-button size="small" type="warning" plain @click="quickZgrab">zgrab 扫描器</el-button>
      </div>

      <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
        <el-select v-model="protocol" placeholder="协议" style="width:160px;">
          <el-option label="不限" value="" />
          <el-option label="HTTP" value="http" />
          <el-option label="SSH" value="ssh" />
        </el-select>

        <el-select v-model="eventType" placeholder="事件类型" style="width:200px;">
          <el-option label="不限" value="" />
          <el-option label="http_request" value="http_request" />
          <el-option label="ssh_login_attempt" value="ssh_login_attempt" />
        </el-select>

        <el-input v-model="srcIp" placeholder="来源 IP" style="width:200px;" />
        <el-input v-model="path" placeholder="HTTP 路径（精确匹配）" style="width:260px;" />
        <el-input v-model="uaContains" placeholder="UA 包含（HTTP）" style="width:240px;" />

        <el-input v-model="sshUser" placeholder="SSH 用户名" style="width:180px;" />
        <el-select v-model="authResult" placeholder="SSH 结果" style="width:160px;">
          <el-option label="不限" value="" />
          <el-option label="失败" value="failed" />
          <el-option label="成功" value="success" />
        </el-select>

        <el-switch v-model="sensitiveOnly" active-text="仅敏感路径" />

        <div style="display:flex; align-items:center; gap:6px;">
          <span style="color:#666;">条数</span>
          <el-input-number v-model="limit" :min="10" :max="2000" :step="50" />
        </div>

        <el-button type="primary" @click="load">查询</el-button>
        <el-button @click="reset">重置</el-button>

        <el-dropdown>
          <el-button type="info" plain>
            导出 <span style="margin-left:4px;">▾</span>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="exportFile('json')">导出 JSON</el-dropdown-item>
              <el-dropdown-item @click="exportFile('csv')">导出 CSV</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div style="color:#888;font-size:12px;margin-top:8px;">
        说明：点击“导出”会按当前过滤条件从后端生成文件（用于论文附录/数据分析）。
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <el-table :data="rows" style="width:100%;">
        <el-table-column label="时间" width="190">
          <template #default="{ row }">{{ formatTime(row.ts) }}</template>
        </el-table-column>

        <el-table-column prop="protocol" label="协议" width="90" />
        <el-table-column prop="event_type" label="类型" width="160" />
        <el-table-column prop="src_ip" label="IP" width="160" />

        <el-table-column label="内容">
          <template #default="{ row }">
            <span v-if="row.protocol==='http'">
              {{ row.payload?.method }} {{ row.payload?.path }}
              <span style="color:#888;">UA={{ (row.payload?.ua || '').slice(0, 50) }}</span>
            </span>
            <span v-else>
              SSH {{ row.payload?.auth_result }} user={{ row.payload?.username }}
              <span style="color:#888;"> client={{ (row.payload?.client_version || '').slice(0, 40) }}</span>
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" @click="goProfile(row.src_ip)">画像</el-button>
            <el-button size="small" type="primary" plain @click="filterByIp(row.src_ip)">筛选该 IP</el-button>
            <el-button size="small" type="info" plain @click="openDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="detailOpen" title="事件详情" width="60%">
        <div v-if="detailRow">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="时间">{{ formatTime(detailRow.ts) }}</el-descriptions-item>
            <el-descriptions-item label="来源 IP">{{ detailRow.src_ip }}</el-descriptions-item>
            <el-descriptions-item label="协议">{{ detailRow.protocol }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ detailRow.event_type }}</el-descriptions-item>
            <el-descriptions-item label="蜜罐">{{ detailRow.honeypot_name }} / {{ detailRow.honeypot_instance_id }}</el-descriptions-item>
            <el-descriptions-item label="来源端口">{{ detailRow.src_port }}</el-descriptions-item>
          </el-descriptions>

          <el-card style="margin-top:12px;" v-if="detailRow.protocol==='http'">
            <div style="font-weight:700;margin-bottom:6px;">HTTP 字段</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="方法">{{ detailRow.payload?.method }}</el-descriptions-item>
              <el-descriptions-item label="路径">{{ detailRow.payload?.path }}</el-descriptions-item>
              <el-descriptions-item label="查询串">{{ detailRow.payload?.query }}</el-descriptions-item>
              <el-descriptions-item label="状态码">{{ detailRow.payload?.status }}</el-descriptions-item>
              <el-descriptions-item label="User-Agent" :span="2">{{ detailRow.payload?.ua }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card style="margin-top:12px;" v-else>
            <div style="font-weight:700;margin-bottom:6px;">SSH 字段</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="用户名">{{ detailRow.payload?.username }}</el-descriptions-item>
              <el-descriptions-item label="结果">{{ detailRow.payload?.auth_result }}</el-descriptions-item>
              <el-descriptions-item label="密码(掩码)">{{ detailRow.payload?.password_masked }}</el-descriptions-item>
              <el-descriptions-item label="客户端版本" :span="2">{{ detailRow.payload?.client_version }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card style="margin-top:12px;">
            <div style="font-weight:700;margin-bottom:6px;">原始 payload</div>
            <pre style="margin:0; background:#111;color:#ddd;padding:12px;overflow:auto;">{{ JSON.stringify(detailRow.payload, null, 2) }}</pre>
          </el-card>
        </div>
      </el-dialog>

      <div style="color:#888;font-size:12px;margin-top:8px;">
        提示：你也可以从“看板”点击 Top Path/Top UA/Top SSH 用户名跳转到此页面自动带条件。
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, loadToken } from "../api/client";
import { msgError, msgSuccess } from "../utils/notify";
import { formatTime } from "../utils/time";

const route = useRoute();
const router = useRouter();

const rows = ref<any[]>([]);

const protocol = ref<string>(String(route.query.protocol || ""));
const eventType = ref<string>(String(route.query.event_type || ""));
const srcIp = ref<string>(String(route.query.src_ip || ""));
const path = ref<string>(String(route.query.path || ""));
const uaContains = ref<string>(String(route.query.ua || ""));
const sshUser = ref<string>(String(route.query.ssh_user || ""));
const authResult = ref<string>(String(route.query.auth_result || ""));
const sensitiveOnly = ref<boolean>(String(route.query.sensitive_only || "") === "true");
const limit = ref<number>(Number(route.query.limit || 200));

const detailOpen = ref(false);
const detailRow = ref<any>(null);

function openDetail(row: any) {
  detailRow.value = row;
  detailOpen.value = true;
}

function goProfile(ip: string) {
  router.push(`/app/profiles/${encodeURIComponent(ip)}`);
}

function filterByIp(ip: string) {
  srcIp.value = ip;
  load();
}

function quickAll() { reset(); load(); }
function quickSensitive() { reset(); protocol.value = "http"; eventType.value = "http_request"; sensitiveOnly.value = true; load(); }
function quickSshBruteforce() { reset(); protocol.value = "ssh"; eventType.value = "ssh_login_attempt"; authResult.value = "failed"; load(); }
function quickZgrab() { reset(); protocol.value = "http"; eventType.value = "http_request"; uaContains.value = "zgrab"; load(); }

function reset() {
  protocol.value = "";
  eventType.value = "";
  srcIp.value = "";
  path.value = "";
  uaContains.value = "";
  sshUser.value = "";
  authResult.value = "";
  sensitiveOnly.value = false;
  limit.value = 200;
}

async function load() {
  loadToken();
  const params: any = { limit: limit.value };
  if (protocol.value) params.protocol = protocol.value;
  if (eventType.value) params.event_type = eventType.value;
  if (srcIp.value) params.src_ip = srcIp.value;
  if (path.value) params.path = path.value;
  if (uaContains.value) params.ua_contains = uaContains.value;
  if (sshUser.value) params.ssh_user = sshUser.value;
  if (authResult.value) params.auth_result = authResult.value;
  if (sensitiveOnly.value) params.sensitive_only = true;

  try {
    const resp = await api.get("/api/events/search", { params });
    rows.value = resp.data;
    msgSuccess(`查询完成：${rows.value.length} 条`);
  } catch (e: any) {
    msgError("查询失败：" + (e?.response?.data?.detail || "未知错误"));
    router.push("/login");
  }
}

async function exportFile(fmt: "json" | "csv") {
  loadToken();
  const params: any = { fmt, limit: Math.min(5000, Math.max(100, limit.value)) };
  if (protocol.value) params.protocol = protocol.value;
  if (eventType.value) params.event_type = eventType.value;
  if (srcIp.value) params.src_ip = srcIp.value;
  if (path.value) params.path = path.value;
  if (uaContains.value) params.ua_contains = uaContains.value;
  if (sshUser.value) params.ssh_user = sshUser.value;
  if (authResult.value) params.auth_result = authResult.value;
  if (sensitiveOnly.value) params.sensitive_only = true;

  try {
    const resp = await api.get("/api/events/export", { params, responseType: "blob" });
    const blob = new Blob([resp.data], { type: fmt === "json" ? "application/json" : "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fmt === "json" ? "events-export.json" : "events-export.csv";
    a.click();
    URL.revokeObjectURL(url);
    msgSuccess("导出已开始下载");
  } catch (e: any) {
    msgError("导出失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

onMounted(load);
</script>