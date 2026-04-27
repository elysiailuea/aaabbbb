<template>
  <div>
    <div style="font-weight:700;margin-bottom:8px;">{{ title }}</div>
    <div style="height:260px;" ref="el"></div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { onMounted, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps<{ title: string; labels: string[]; values: number[] }>();
const emit = defineEmits<{ (e: "bar-click", label: string): void }>();

const el = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

function render() {
  if (!chart) return;
  chart.setOption({
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 50, right: 20, top: 10, bottom: 40 },
    xAxis: { type: "category", data: props.labels, axisLabel: { rotate: 25 } },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: props.values }],
  });
  chart.off("click");
  chart.on("click", (p: any) => {
    if (p?.name) emit("bar-click", String(p.name));
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

watch(() => [props.labels, props.values], render, { deep: true });

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
});
</script>