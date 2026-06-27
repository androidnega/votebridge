import { onMounted, onUnmounted, ref } from "vue";

const QUERIES = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
};

function getBreakpoint() {
  const width = window.innerWidth;
  if (width >= QUERIES["2xl"]) return "2xl";
  if (width >= QUERIES.xl) return "xl";
  if (width >= QUERIES.lg) return "lg";
  if (width >= QUERIES.md) return "md";
  if (width >= QUERIES.sm) return "sm";
  return "xs";
}

export function useBreakpoints() {
  const breakpoint = ref(getBreakpoint());
  const isMobile = ref(window.innerWidth < QUERIES.lg);
  const isDesktop = ref(window.innerWidth >= QUERIES.lg);

  function update() {
    breakpoint.value = getBreakpoint();
    isMobile.value = window.innerWidth < QUERIES.lg;
    isDesktop.value = window.innerWidth >= QUERIES.lg;
  }

  onMounted(() => {
    window.addEventListener("resize", update);
  });

  onUnmounted(() => {
    window.removeEventListener("resize", update);
  });

  return { breakpoint, isMobile, isDesktop, QUERIES };
}
