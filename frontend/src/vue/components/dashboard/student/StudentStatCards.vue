<script setup>
import { computed } from "vue";
import { FaIcon } from "@/components/ui";

const props = defineProps({
  activeCount: { type: Number, default: 0 },
  votesCast: { type: Number, default: 0 },
  closesIn: { type: String, default: "—" },
});

const stats = computed(() => [
  {
    id: "active",
    icon: "fa-square-poll-vertical",
    shortLabel: "Active",
    label: "Active elections",
    value: props.activeCount,
  },
  {
    id: "votes",
    icon: "fa-square-check",
    shortLabel: "Votes",
    label: "Votes cast this season",
    value: props.votesCast,
  },
  {
    id: "closes",
    icon: "fa-clock",
    shortLabel: "Closes in",
    label: "Voting closes in",
    value: props.closesIn,
    isCountdown: true,
  },
]);
</script>

<template>
  <section class="mb-6 grid w-full grid-cols-3 gap-2 sm:gap-3" aria-label="Election summary">
    <article
      v-for="stat in stats"
      :key="stat.id"
      class="flex min-h-[88px] min-w-0 items-center gap-2.5 rounded-lg border border-border bg-white px-3 py-4 sm:min-h-[96px] sm:gap-3 sm:px-4 sm:py-5"
      :aria-label="stat.label"
    >
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface-muted text-brand-700 sm:h-10 sm:w-10"
        aria-hidden="true"
      >
        <FaIcon :icon="stat.icon" :fixed-width="false" class="text-xs sm:text-sm" />
      </div>

      <div class="min-w-0 flex-1">
        <p
          class="truncate text-lg font-bold tabular-nums leading-none text-ink-primary sm:text-2xl"
          :class="stat.isCountdown ? 'text-sm sm:text-lg' : ''"
          :aria-live="stat.isCountdown ? 'polite' : undefined"
        >
          {{ stat.value }}
        </p>
        <p class="mt-1.5 truncate text-[10px] font-medium text-ink-secondary sm:text-xs">
          <span class="sm:hidden">{{ stat.shortLabel }}</span>
          <span class="hidden sm:inline">{{ stat.label }}</span>
        </p>
      </div>
    </article>
  </section>
</template>
