<script setup>
import { computed } from "vue";
import { useCountdown } from "@/composables/useCountdown";

const props = defineProps({
  startDate: String,
  endDate: String,
  status: String,
});

const countdownTarget = computed(() => {
  if (props.status === "scheduled" && props.startDate) return props.startDate;
  if (["open", "paused"].includes(props.status) && props.endDate) return props.endDate;
  return null;
});

const countdownLabel = computed(() => {
  if (props.status === "scheduled") return "Opens in";
  if (["open", "paused"].includes(props.status)) return "Closes in";
  return "Time remaining";
});

const remaining = useCountdown(countdownTarget);

const showCountdown = computed(
  () => countdownTarget.value && remaining.value && !remaining.value.isEnded
);

const pad = (value) => String(value).padStart(2, "0");
</script>

<template>
  <div
    v-if="showCountdown"
    class="rounded-xl bg-white/10 px-4 py-3 backdrop-blur-sm ring-1 ring-white/20"
    role="timer"
    :aria-label="`${countdownLabel}: ${remaining.days} days ${remaining.hours} hours`"
  >
    <p class="text-xs font-medium uppercase tracking-wide text-brand-100">{{ countdownLabel }}</p>
    <div class="mt-2 flex flex-wrap gap-3 sm:gap-4">
      <div v-if="remaining.days > 0" class="text-center">
        <span class="block text-2xl font-bold tabular-nums">{{ remaining.days }}</span>
        <span class="text-xs text-brand-100">days</span>
      </div>
      <div class="text-center">
        <span class="block text-2xl font-bold tabular-nums">{{ pad(remaining.hours) }}</span>
        <span class="text-xs text-brand-100">hrs</span>
      </div>
      <div class="text-center">
        <span class="block text-2xl font-bold tabular-nums">{{ pad(remaining.minutes) }}</span>
        <span class="text-xs text-brand-100">min</span>
      </div>
      <div class="text-center">
        <span class="block text-2xl font-bold tabular-nums">{{ pad(remaining.seconds) }}</span>
        <span class="text-xs text-brand-100">sec</span>
      </div>
    </div>
  </div>
  <p v-else-if="status === 'closed'" class="text-sm text-brand-100">Voting has ended.</p>
</template>
