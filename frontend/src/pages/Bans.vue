<template>
  <div style="padding: 12px;">
    <el-card>
      <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <el-input v-model="ip" placeholder="要封禁的 IP" style="max-width:220px;" />
        <el-input v-model="reason" placeholder="原因（例如：手动封禁/自动高危）" style="max-width:280px;" />
        <div style="display:flex; align-items:center; gap:6px;">
          <span style="color:#666;">TTL(秒)</span>
          <el-input-number v-model="ttl" :min="60" :step="60" />
        </div>
        <el-button type="danger" @click="createBan">封禁</el-button>
        <el-button @click="loadAll">刷新</el-button>
      </div>

      <div style="margin-top:10px; color:#666; font-size:12px; line-height:1.6;">
        <div>
          生效机制：封禁写入后端数据库后，由 <b>blocker 网关</b> 定时拉取并在容器内通过 <b>ipset/iptables</b> 执行 L2 丢弃（DROP）。
        </div>
        <div>
          白名单：命中白名单的 IP/网段 <b>不会下发到 blocker</b>（避免误封内网/本机）。当前白名单如下：
        </div>
        <div style="margin-top:6px; background:#f7f7f7; padding:8px; border:1px solid #eee; border-radius:4px;">
          {{ whitelistCsv || "（加载中）" }}
        </div>
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <el-table :data="bans" style="width: 100%">
        <el-table-column prop="src_ip" label="IP" width="160" />
        <el-table-column prop="level" label="级别" width="120" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column label="创建时间" width="190">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="到期时间" width="190">
          <template #default="{ row }">{{ formatTime(row.expires_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button size="small" @click="revoke(row.id)" :disabled="row.status !== 'active'">解封</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="color:#666; margin-top:10px;">
        权限说明：管理员/安全员可封禁与解封；只读用户仅能查看。
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, loadToken } from "../api/client";
import { useRouter } from "vue-router";
import { msgError, msgSuccess } from "../utils/notify";
import { formatTime } from "../utils/time";

const router = useRouter();
const bans = ref<any[]>([]);
const ip = ref("");
const reason = ref("manual");
const ttl = ref(3600);
const whitelistCsv = ref("");

async function loadWhitelist() {
  try {
    const resp = await api.get("/api/blocker/settings");
    whitelistCsv.value = resp.data.block_whitelist_csv || "";
  } catch {
    whitelistCsv.value = "（无法获取白名单：blocker/settings 请求失败）";
  }
}

async function loadBans() {
  loadToken();
  try {
    const resp = await api.get("/api/bans");
    bans.value = resp.data;
  } catch {
    router.push("/login");
  }
}

async function loadAll() {
  await Promise.all([loadWhitelist(), loadBans()]);
}

async function createBan() {
  loadToken();
  try {
    await api.post("/api/bans", { src_ip: ip.value, reason: reason.value, level: "high", ttl_seconds: ttl.value, evidence: {} });
    ip.value = "";
    msgSuccess("封禁已提交（blocker 将在下次同步时生效）");
    await loadBans();
  } catch (e: any) {
    msgError("操作失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

async function revoke(id: string) {
  loadToken();
  try {
    await api.post(`/api/bans/${id}/revoke`);
    msgSuccess("已解封（blocker 将在下次同步时生效）");
    await loadBans();
  } catch (e: any) {
    msgError("操作失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

onMounted(loadAll);
</script>