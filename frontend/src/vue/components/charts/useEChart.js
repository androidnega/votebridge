import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from "vue";

export const CHART_COLORS = ["#1E3A6E", "#334155", "#2E7D32", "#0F766E", "#CA8A04", "#C62828"];

let echartsPromise = null;

function loadEcharts() {
  if (!echartsPromise) {
    echartsPromise = import("echarts/core").then(async (echarts) => {
      const [{ BarChart, GaugeChart, HeatmapChart, LineChart, PieChart }, components, { CanvasRenderer }] =
        await Promise.all([
          import("echarts/charts"),
          import("echarts/components"),
          import("echarts/renderers"),
        ]);
      echarts.use([
        LineChart,
        BarChart,
        PieChart,
        GaugeChart,
        HeatmapChart,
        components.GridComponent,
        components.LegendComponent,
        components.TitleComponent,
        components.TooltipComponent,
        components.VisualMapComponent,
        CanvasRenderer,
      ]);
      return echarts;
    });
  }
  return echartsPromise;
}

export function useEChart(optionRef) {
  const elRef = ref(null);
  const chart = shallowRef(null);
  const ready = ref(false);

  async function render() {
    if (!elRef.value || !optionRef.value) return;
    const echarts = await loadEcharts();
    ready.value = true;
    if (!chart.value) {
      chart.value = echarts.init(elRef.value, null, { renderer: "canvas" });
    }
    chart.value.setOption(optionRef.value, { notMerge: true });
    chart.value.resize();
  }

  function onResize() {
    chart.value?.resize();
  }

  onMounted(() => {
    render();
    window.addEventListener("resize", onResize);
  });

  watch(optionRef, () => render(), { deep: true });

  onBeforeUnmount(() => {
    window.removeEventListener("resize", onResize);
    chart.value?.dispose();
    chart.value = null;
  });

  return { elRef, ready, render };
}
