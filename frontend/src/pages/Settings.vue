<template>
  <div style="padding:12px;">
    <el-card>
      <div style="font-weight:800;margin-bottom:8px;">策略配置</div>
      <div style="color:#666;font-size:12px;">
        说明：仅管理员可修改。用于演示“策略可调 -> 告警/封禁行为变化”。
      </div>
      <div style="margin-top:10px; display:flex; gap:8px;">
        <el-button @click="load">刷新</el-button>
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <el-table :data="rows" style="width:100%;">
        <el-table-column prop="key" label="键" width="260" />
        <el-table-column label="值">
          <template #default="{ row }">
            <div v-if="row.bool_value !== null && row.bool_value !== undefined">
              <el-switch v-model="row.bool_value" />
            </div>
            <div v-else-if="row.int_value !== null && row.int_value !== undefined">
              <el-input-number v-model="row.int_value" />
            </div>
            <div v-else>
              <el-input v-model="row.str_value" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="save(row)">保存</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="color:#888;font-size:12px;margin-top:10px;">
        推荐演示：关闭 auto_ban_enabled 后，critical 只告警不封禁；调整 auto_ban_ttl_seconds 观察到期时间变化。
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { api, loadToken } from "../api/client";
import { msgError, msgSuccess } from "../utils/notify";

const router = useRouter();
const rows = ref<any[]>([]);

async function load() {
  loadToken();
  try {
    const resp = await api.get("/api/settings");
    rows.value = resp.data;
  } catch {
    router.push("/login");
  }
}

async function save(row: any) {
  loadToken();
  const body: any = {};
  if (row.bool_value !== null && row.bool_value !== undefined) body.bool_value = row.bool_value;
  if (row.int_value !== null && row.int_value !== undefined) body.int_value = row.int_value;
  if (row.str_value !== null && row.str_value !== undefined) body.str_value = row.str_value;

  try {
    await api.put(`/api/settings/${encodeURIComponent(row.key)}`, body);
    msgSuccess("保存成功");
  } catch (e: any) {
    msgError("保存失败：" + (e?.response?.data?.detail || "未知错误"));
  }
}

onMounted(load);
</script>