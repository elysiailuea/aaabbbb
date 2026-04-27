<template>
  <div style="height:220px;" ref="el"></div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { onMounted, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps<{ title: string; series: { t: string; count: number }[]; color: string }>();
const el = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

function render() {
  if (!chart) return;
  chart.setOption({
    title: { text: props.title, left: "center", textStyle: { fontSize: 12 } },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: props.series.map((x) => x.t.slice(11, 16)) },
    yAxis: { type: "value" },
    series: [{ type: "line", data: props.series.map((x) => x.count), smooth: true, lineStyle: { color: props.color } }],
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