<template>
  <div style="padding:12px;">
    <el-card>
      <div style="font-weight:800;">演示模式</div>
      <div style="color:#666;font-size:12px;margin-top:6px; line-height:1.7;">
        点击“生成演示数据”后，后端写入模拟攻击事件并触发聚合任务。
        <br />
        点击“清空演示数据”只会清理 <b>demo-http / demo-ssh</b> 产生的事件，以及演示 IP 对应的画像/告警（可选是否清理封禁）。
        <br />
        注意：接口限制为 <b>管理员</b> 才可使用。
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
        <el-input v-model="ip" placeholder="指定攻击者 IP（可选，例如 203.0.113.10）" style="width:320px;" />

        <div style="display:flex; align-items:center; gap:6px;">
          <span style="color:#666;">时间范围(分钟)</span>
          <el-input-number v-model="minutes" :min="5" :max="120" :step="5" />
        </div>

        <div style="display:flex; align-items:center; gap:6px;">
          <span style="color:#666;">HTTP 事件数</span>
          <el-input-number v-model="httpEvents" :min="50" :max="2000" :step="50" />
        </div>

        <div style="display:flex; align-items:center; gap:6px;">
          <span style="color:#666;">SSH 尝试数</span>
          <el-input-number v-model="sshEvents" :min="10" :max="800" :step="10" />
        </div>

        <el-button type="danger" @click="seed" :loading="loadingSeed">一键生成演示数据</el-button>

        <el-popconfirm
          title="确定要清空演示数据吗？（不会影响真实蜜罐数据）"
          confirm-button-text="确定清空"
          cancel-button-text="取消"
          @confirm="purge"
        >
          <template #reference>
            <el-button type="warning" plain :loading="loadingPurge">清空演示数据</el-button>
          </template>
        </el-popconfirm>

        <el-button type="primary" plain @click="go('/app/dashboard')">打开看板</el-button>
        <el-button type="primary" plain @click="go('/app/alerts')">打开告警</el-button>
        <el-button type="primary" plain @click="go('/app/events')">打开事件查询</el-button>
        <el-button type="primary" plain @click="go('/app/bans')">封禁管理</el-button>
        <el-button type="primary" plain @click="go('/app/system')">系统状态</el-button>
      </div>

      <div style="margin-top:10px; display:flex; gap:14px; flex-wrap:wrap; align-items:center;">
        <el-checkbox v-model="purgeProfiles">同时清理画像</el-checkbox>
        <el-checkbox v-model="purgeAlerts">同时清理告警</el-checkbox>
        <el-checkbox v-model="purgeBans">同时清理封禁（不建议默认勾选）</el-checkbox>
        <span style="color:#888;font-size:12px;">
          提示：默认不清理封禁，避免你演示完自动封禁后记录突然消失；可手动解封或等待 TTL 到期。
        </span>
      </div>

      <div style="color:#888;font-size:12px;margin-top:10px;">
        建议演示顺序：先打开“系统状态”确认正常 → 点击生成 → 等待 5~30 秒 → 看板/告警/封禁变化。
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <div style="font-weight:700;margin-bottom:8px;">最近一次执行结果</div>
      <pre style="margin:0; background:#111;color:#ddd;padding:12px;overflow:auto;">{{ JSON.stringify(result, null, 2) }}</pre>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api, loadToken } from "../api/client";
import { msgError, msgSuccess } from "../utils/notify";

const router = useRouter();
function go(p: string) { router.push(p); }

const ip = ref("");
const minutes = ref(30);
const httpEvents = ref(200);
const sshEvents = ref(60);

const purgeProfiles = ref(true);
const purgeAlerts = ref(true);
const purgeBans = ref(false);

const loadingSeed = ref(false);
const loadingPurge = ref(false);
const result = ref<any>({});

async function seed() {
  loadToken();
  loadingSeed.value = true;
  try {
    const payload: any = { minutes: minutes.value, http_events: httpEvents.value, ssh_events: sshEvents.value };
    if (ip.value.trim()) payload.ip = ip.value.trim();
    const resp = await api.post("/api/demo/seed", payload);
    result.value = resp.data;
    msgSuccess("已提交演示数据生成（稍等片刻查看看板/告警）");
  } catch (e: any) {
    msgError("执行失败：" + (e?.response?.data?.detail || "未知错误"));
  } finally {
    loadingSeed.value = false;
  }
}

async function purge() {
  loadToken();
  loadingPurge.value = true;
  try {
    const payload: any = { purge_profiles: purgeProfiles.value, purge_alerts: purgeAlerts.value, purge_bans: purgeBans.value };
    const resp = await api.post("/api/demo/purge", payload);
    result.value = resp.data;
    msgSuccess("已清空演示数据");
  } catch (e: any) {
    msgError("清空失败：" + (e?.response?.data?.detail || "未知错误"));
  } finally {
    loadingPurge.value = false;
  }
}
</script>