<template>
  <div style="padding:12px;">
    <el-card>
      <div style="font-weight:800;">告警规则说明（论文/答辩用）</div>
      <div style="color:#666;font-size:12px;margin-top:6px;">
        本页面用于解释系统的风险评分与告警生成逻辑，便于答辩时展示“为什么会告警/为什么会封禁”。
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <h3 style="margin:0 0 10px 0;">1. 数据来源</h3>
      <ul style="margin:0; color:#333; line-height:1.8;">
        <li>HTTP 蜜罐：记录任意路径请求（方法/路径/UA/状态码）。</li>
        <li>SSH 蜜罐（Cowrie）：记录登录尝试（用户名、结果、客户端版本）。</li>
      </ul>
    </el-card>

    <el-card style="margin-top:12px;">
      <h3 style="margin:0 0 10px 0;">2. 攻击画像聚合（每 30 秒定时）</h3>
      <ul style="margin:0; color:#333; line-height:1.8;">
        <li>按 IP 聚合近 1 小时事件：HTTP 数量、SSH 失败次数、峰值 RPM。</li>
        <li>统计 Top HTTP 路径、Top SSH 用户名、生成指纹 fingerprint（用于去重）。</li>
      </ul>
    </el-card>

    <el-card style="margin-top:12px;">
      <h3 style="margin:0 0 10px 0;">3. 风险评分（示例规则，可在策略配置调整敏感路径字典）</h3>
      <table style="width:100%; border-collapse:collapse;">
        <tr>
          <th style="border:1px solid #eee;padding:8px;">规则</th>
          <th style="border:1px solid #eee;padding:8px;">加分</th>
          <th style="border:1px solid #eee;padding:8px;">解释</th>
        </tr>
        <tr>
          <td style="border:1px solid #eee;padding:8px;">命中敏感路径（如 /.env）</td>
          <td style="border:1px solid #eee;padding:8px;">+35</td>
          <td style="border:1px solid #eee;padding:8px;">典型漏洞探测/扫描行为</td>
        </tr>
        <tr>
          <td style="border:1px solid #eee;padding:8px;">高频扫描（>120 rpm）</td>
          <td style="border:1px solid #eee;padding:8px;">+25</td>
          <td style="border:1px solid #eee;padding:8px;">自动化扫描器特征明显</td>
        </tr>
        <tr>
          <td style="border:1px solid #eee;padding:8px;">HTTP 总量高（>500/h）</td>
          <td style="border:1px solid #eee;padding:8px;">+15</td>
          <td style="border:1px solid #eee;padding:8px;">大规模探测/字典攻击</td>
        </tr>
        <tr>
          <td style="border:1px solid #eee;padding:8px;">SSH 爆破（失败≥20/h）</td>
          <td style="border:1px solid #eee;padding:8px;">+35</td>
          <td style="border:1px solid #eee;padding:8px;">典型口令爆破行为</td>
        </tr>
        <tr>
          <td style="border:1px solid #eee;padding:8px;">命中高危用户名（root/admin/test/oracle）</td>
          <td style="border:1px solid #eee;padding:8px;">+10</td>
          <td style="border:1px solid #eee;padding:8px;">攻击者偏好高权限账户</td>
        </tr>
      </table>

      <div style="color:#666;font-size:12px;margin-top:10px;">
        评分结果映射风险等级：0-29 低风险，30-59 中风险，60-79 高风险，80-100 严重（critical）。
      </div>
    </el-card>

    <el-card style="margin-top:12px;">
      <h3 style="margin:0 0 10px 0;">4. 告警去重（时间窗）</h3>
      <ul style="margin:0; color:#333; line-height:1.8;">
        <li>去重键：<b>src_ip + alert_type + fingerprint</b></li>
        <li>时间窗：默认 10 分钟（可在策略配置中调整）。</li>
        <li>窗内重复命中会更新：hit_count、window_end、evidence。</li>
      </ul>
    </el-card>

    <el-card style="margin-top:12px;">
      <h3 style="margin:0 0 10px 0;">5. 自动封禁联动（L2）</h3>
      <ul style="margin:0; color:#333; line-height:1.8;">
        <li>当风险等级为 <b>critical</b> 且开启 auto_ban_enabled 时，系统自动写入封禁记录。</li>
        <li>blocker 网关周期性拉取活动封禁列表，并在容器内通过 ipset/iptables 执行 DROP。</li>
        <li>白名单命中则不下发（避免误封内��/本机）。</li>
      </ul>
    </el-card>
  </div>
</template>