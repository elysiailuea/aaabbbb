<template>
  <div style="padding:12px;">
    <el-card>
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
        <div>
          <div style="font-weight:800;">总览看板</div>
          <div style="color:#666;font-size:12px;">
            画像/告警/封禁由后台定时任务自动聚合；此页面用于安全运营态势展示。
          </div>
        </div>
        <div style="display:flex; gap:8px;">
          <el-button @click="load">刷新</el-button>
          <el-button type="primary" plain @click="go('/app/events')">事件查询</el-button>
          <el-button type="primary" plain @click="go('/app/alerts')">告警中心</el-button>
          <el-button type="danger" plain @click="go('/app/bans')">封禁管理</el-button>
        </div>
      </div>
    </el-card>

    <div style="display:grid;grid-template-columns:repeat(6, minmax(0, 1fr));gap:12px;margin-top:12px;">
      <el-card><div style="color:#666;">近 1 小时事件</div><div style="font-size:26px;font-weight:700;">{{ stats.events_1h }}</div></el-card>
      <el-card><div style="color:#666;">近 24 小时事件</div><div style="font-size:26px;font-weight:700;">{{ stats.events_24h }}</div></el-card>
      <el-card><div style="color:#666;">近 24 小时 HTTP</div><div style="font-size:26px;font-weight:700;">{{ stats.http_24h }}</div></el-card>
      <el-card><div style="color:#666;">近 24 小时 SSH</div><div style="font-size:26px;font-weight:700;">{{ stats.ssh_24h }}</div></el-card>
      <el-card><div style="color:#666;">未关闭告警</div><div style="font-size:26px;font-weight:700;">{{ stats.alerts_open }}</div></el-card>
      <el-card><div style="color:#666;">生效封禁</div><div style="font-size:26px;font-weight:700;">{{ stats.bans_active }}</div></el-card>
    </div>

    <div style="display:grid;grid-template-columns:repeat(2, minmax(0, 1fr));gap:12px;margin-top:12px;">
      <el-card>
        <TrendChart :series="trendAll" />
      </el-card>
      <el-card>
        <PieChart title="未关闭告警：按级别分布" :items="alertsPie" />
      </el-card>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:12px;margin-top:12px;">
      <el-card>
        <TrendChartSmall title="HTTP：每分钟事件数" :series="trendHttp" color="#409eff" />
      </el-card>
      <el-card>
        <TrendChartSmall title="SSH：每分钟事件数" :series="trendSsh" color="#67c23a" />
      </el-card>
      <el-card>
        <TrendChartSmall title="SSH：失败登录/分钟" :series="trendSshFail" color="#f56c6c" />
      </el-card>
    </div>

    <div style="display:grid;grid-template-columns:repeat(2, minmax(0, 1fr));gap:12px;margin-top:12px;">
      <el-card>
        <TopBarChart
          title="Top 来源 IP（近 1 小时，点击查看画像）"
          :labels="topIps.map(x => x.ip)"
          :values="topIps.map(x => x.count)"
          @bar-click="onIpClick"
        />
        <div style="color:#888;font-size:12px;margin-top:6px;">
          点击某个 IP 可直接跳转到该攻击者画像详情。
        </div>
      </el-card>

      <el-card>
        <TopBarChart
          title="Top HTTP 路径（近 1 小时，点击查看事件）"
          :labels="topPaths.map(x => x.path)"
          :values="topPaths.map(x => x.count)"
          @bar-click="onPathClick"
        />
        <div style="color:#888;font-size:12px;margin-top:6px;">
          点击路径可带条件跳转到“事件查询”，用于查看该路径的扫描详情。
        </div>
      </el-card>
    </div>

    <div style="display:grid;grid-template-columns:repeat(2, minmax(0, 1fr));gap:12px;margin-top:12px;">
      <el-card>
        <TopBarChart
          title="Top HTTP User-Agent（近 1 小时，点击过滤事件）"
          :labels="topUas.map(x => shortUa(x.ua))"
          :values="topUas.map(x => x.count)"
          @bar-click="onUaClick"
        />
        <div style="color:#888;font-size:12px;margin-top:6px;">
          说明：展示会对 UA 文本做截断；点击后使用“包含匹配”过滤。
        </div>
      </el-card>

      <el-card>
        <TopBarChart
          title="Top SSH 用户名（失败登录，近 1 小时，点击过滤事件）"
          :labels="topSshUsers.map(x => x.username)"
          :values="topSshUsers.map(x => x.count)"
          @bar-click="onSshUserClick"
        />
        <div style="color:#888;font-size:12px;margin-top:6px;">
          用于展示爆破字典特征（如 root/admin/test 等）。
        </div>
      </el-card>
    </div>

    <div style="color:#888;font-size:12px;margin-top:10px;">
      数据生成时间：{{ generatedAt }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { loadToken } from "../api/client";
import { fetchDashboard } from "../api/dashboard";
import TrendChart from "../components/TrendChart.vue";
import TopBarChart from "../components/TopBarChart.vue";
import PieChart from "../components/PieChart.vue";
import TrendChartSmall from "../components/TrendChartSmall.vue";
import { msgError, msgInfo } from "../utils/notify";

const router = useRouter();
function go(p: string) { router.push(p); }

const generatedAt = ref("");
const stats = ref({ events_1h: 0, events_24h: 0, http_24h: 0, ssh_24h: 0, alerts_open: 0, bans_active: 0 });

const trendAll = ref<{ t: string; count: number }[]>([]);
const trendHttp = ref<{ t: string; count: number }[]>([]);
const trendSsh = ref<{ t: string; count: number }[]>([]);
const trendSshFail = ref<{ t: string; count: number }[]>([]);

const topIps = ref<{ ip: string; count: number }[]>([]);
const topPaths = ref<{ path: string; count: number }[]>([]);
const topUas = ref<{ ua: string; count: number }[]>([]);
const topSshUsers = ref<{ username: string; count: number }[]>([]);
const alertsPie = ref<{ name: string; value: number }[]>([]);

async function load() {
  loadToken();
  try {
    const data = await fetchDashboard();
    generatedAt.value = data.generated_at;
    stats.value = data.stats;

    trendAll.value = data.trend.all;
    trendHttp.value = data.trend.http;
    trendSsh.value = data.trend.ssh;
    trendSshFail.value = data.trend.ssh_fail;

    topIps.value = data.top_ips_1h;
    topPaths.value = data.top_paths_1h;
    topUas.value = data.top_uas_1h || [];
    topSshUsers.value = data.top_ssh_usernames_1h || [];
    alertsPie.value = (data.alerts_by_level_open || []).map((x: any) => ({ name: x.level, value: x.count }));
  } catch (e: any) {
    msgError("加载看板失败：" + (e?.response?.data?.detail || "请重新登录"));
    router.push("/login");
  }
}

function onIpClick(label: string) {
  router.push(`/app/profiles/${encodeURIComponent(label)}`);
}

function onPathClick(label: string) {
  router.push({ path: "/app/events", query: { protocol: "http", event_type: "http_request", path: label, limit: "200" } });
}

function shortUa(ua: string) {
  if (!ua) return "(空)";
  return ua.length > 24 ? ua.slice(0, 24) + "…" : ua;
}

function onUaClick(shortLabel: string) {
  const sub = shortLabel.replace("…", "");
  if (!sub || sub === "(空)") { msgInfo("该条 UA 为空，无法过滤"); return; }
  router.push({ path: "/app/events", query: { protocol: "http", event_type: "http_request", ua: sub, limit: "200" } });
}

function onSshUserClick(username: string) {
  router.push({ path: "/app/events", query: { protocol: "ssh", event_type: "ssh_login_attempt", ssh_user: username, auth_result: "failed", limit: "200" } });
}

onMounted(load);
</script>