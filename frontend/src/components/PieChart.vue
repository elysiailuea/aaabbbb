<template>
  <div style="height:260px;" ref="el"></div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { onMounted, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps<{ title: string; items: { name: string; value: number }[] }>();
const el = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

function render() {
  if (!chart) return;
  chart.setOption({
    title: { text: props.title, left: "center" },
    tooltip: { trigger: "item" },
    series: [
      {
        type: "pie",
        radius: "60%",
        data: props.items,
      },
    ],
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

watch(() => props.items, render, { deep: true });

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
});
</script>