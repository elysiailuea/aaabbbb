<template>
  <div style="height:260px;" ref="el"></div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { onMounted, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps<{ series: { t: string; count: number }[] }>();
const el = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

function render() {
  if (!chart) return;
  chart.setOption({
    title: { text: "近 1 小时事件趋势（总）", left: "center" },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: props.series.map((x) => x.t.slice(11, 16)) },
    yAxis: { type: "value" },
    series: [{ type: "line", data: props.series.map((x) => x.count), smooth: true }],
  });
}

onMounted(() => {
  if (el.value) chart = echarts.init(el.value);
  render();
  window.addEventListener("resize", resize);
});

function resize() {
  chart?.resize();
}

watch(() => props.series, render, { deep: true });

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
});
</script>