<script setup>
import { computed } from "vue";
import { useCountdown } from "@/composables/useCountdown";

const props = defineProps({
  startDate: String,
  endDate: String,
  status: String,
  variant: {
    type: String,
    default: "dark",
    validator: (value) => ["dark", "light"].includes(value),
  },
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

const shellClass = computed(() =>
  props.variant === "light"
    ? "rounded-xl border border-border bg-slate-50 px-4 py-3 shadow-sm"
    : "rounded-xl bg-white/10 px-4 py-3 backdrop-blur-sm ring-1 ring-white/20"
);

const labelClass = computed(() =>
  props.variant === "light"
    ? "text-xs font-medium uppercase tracking-wide text-slate-500"
    : "text-xs font-medium uppercase tracking-wide text-brand-100"
);

const unitClass = computed(() =>
  props.variant === "light" ? "text-xs text-slate-500" : "text-xs text-brand-100"
);

const valueClass = computed(() =>
  props.variant === "light" ? "block text-2xl font-bold tabular-nums text-slate-900" : "block text-2xl font-bold tabular-nums"
);

const endedClass = computed(() =>
  props.variant === "light" ? "text-sm text-slate-600" : "text-sm text-brand-100"
);
</script>

<template>
  <div
    v-if="showCountdown"
    :class="shellClass"
    role="timer"
    :aria-label="`${countdownLabel}: ${remaining.days} days ${remaining.hours} hours`"
  >
    <p :class="labelClass">{{ countdownLabel }}</p>
    <div class="mt-2 flex flex-wrap gap-3 sm:gap-4">
      <div v-if="remaining.days > 0" class="text-center">
        <span :class="valueClass">{{ remaining.days }}</span>
        <span :class="unitClass">days</span>
      </div>
      <div class="text-center">
        <span :class="valueClass">{{ pad(remaining.hours) }}</span>
        <span :class="unitClass">hrs</span>
      </div>
      <div class="text-center">
        <span :class="valueClass">{{ pad(remaining.minutes) }}</span>
        <span :class="unitClass">min</span>
      </div>
      <div class="text-center">
        <span :class="valueClass">{{ pad(remaining.seconds) }}</span>
        <span :class="unitClass">sec</span>
      </div>
    </div>
  </div>
  <p v-else-if="status === 'closed'" :class="endedClass">Voting has ended.</p>
</template>
