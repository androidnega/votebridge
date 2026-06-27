import { onUnmounted, ref, unref, watch } from "vue";

function computeRemaining(target) {
  if (!target) return null;
  const end = new Date(target).getTime();
  if (Number.isNaN(end)) return null;

  const diff = end - Date.now();
  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, totalMs: 0, isEnded: true };
  }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((diff / (1000 * 60)) % 60);
  const seconds = Math.floor((diff / 1000) % 60);

  return { days, hours, minutes, seconds, totalMs: diff, isEnded: false };
}

export function useCountdown(targetDate) {
  const remaining = ref(computeRemaining(targetDate));
  let timer;

  function tick() {
    remaining.value = computeRemaining(unref(targetDate));
  }

  watch(
    () => unref(targetDate),
    () => {
      tick();
    },
    { immediate: true }
  );

  timer = setInterval(tick, 1000);

  onUnmounted(() => {
    clearInterval(timer);
  });

  return remaining;
}
