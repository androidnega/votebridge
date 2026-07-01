<script setup>
import { computed } from "vue";
import { StatusBadge } from "@/components/ui";

const props = defineProps({
  greeting: { type: String, default: "Good morning" },
  name: { type: String, default: "" },
  subtitle: { type: String, default: "Here's the current status of the election platform." },
  dateLabel: { type: String, default: "" },
  phaseLabel: { type: String, default: "" },
  phaseStatus: { type: String, default: "draft" },
  isLive: Boolean,
});

const displayName = computed(() => (props.name ? `, ${props.name}` : ""));
</script>

<template>
  <section class="rounded-2xl border border-border bg-white p-6 shadow-[0_1px_2px_0_rgb(15_23_42_/_0.04)]">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="min-w-0">
        <h2 class="text-xl font-semibold tracking-tight text-ink-primary sm:text-2xl">
          {{ greeting }}{{ displayName }}.
        </h2>
        <p class="mt-1.5 text-sm text-ink-secondary">{{ subtitle }}</p>
        <div class="mt-3 flex flex-wrap items-center gap-2">
          <span v-if="dateLabel" class="text-xs font-medium text-ink-secondary">{{ dateLabel }}</span>
          <StatusBadge v-if="phaseLabel" :status="phaseStatus" :label="phaseLabel" />
          <span
            v-if="isLive"
            class="inline-flex items-center gap-1.5 rounded-full bg-[#E8F5EE] px-2.5 py-0.5 text-xs font-semibold text-[#166534]"
          >
            <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-[#166534]" aria-hidden="true" />
            Live
          </span>
        </div>
      </div>
      <slot name="actions" />
    </div>
  </section>
</template>
