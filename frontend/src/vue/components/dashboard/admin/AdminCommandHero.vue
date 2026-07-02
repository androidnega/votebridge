<script setup>
import { StatusBadge, VButton } from "@/components/ui";
import AdminCountdownStrip from "./AdminCountdownStrip.vue";

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  institution: { type: String, default: "" },
  status: { type: String, default: "draft" },
  statusLabel: { type: String, default: "" },
  isLive: Boolean,
  countdownLabel: { type: String, default: "" },
  countdownParts: {
    type: Object,
    default: () => ({ days: 0, hours: 0, minutes: 0, seconds: 0 }),
  },
  showCountdown: { type: Boolean, default: true },
});

defineEmits(["primary", "secondary"]);
</script>

<template>
  <section
    class="relative overflow-hidden rounded-card border border-border bg-brand-700 shadow-[0_8px_30px_-12px_rgb(15_23_42_/_0.18)]"
  >
    <div class="relative grid gap-6 p-6 lg:grid-cols-[1fr_auto] lg:items-center lg:p-8">
      <div class="min-w-0 text-white">
        <p v-if="institution" class="text-xs font-semibold uppercase tracking-[0.18em] text-white/70">
          {{ institution }}
        </p>
        <h1 class="mt-2 text-2xl font-bold tracking-tight sm:text-3xl lg:text-[2rem] lg:leading-tight">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="mt-2 max-w-2xl text-sm leading-relaxed text-white/80 sm:text-base">
          {{ subtitle }}
        </p>

        <div class="mt-4 flex flex-wrap items-center gap-2">
          <StatusBadge v-if="statusLabel" :status="status" :label="statusLabel" />
          <span
            v-if="isLive"
            class="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold text-white"
          >
            <span class="h-2 w-2 animate-pulse rounded-full bg-emerald-300" aria-hidden="true" />
            Live monitoring
          </span>
        </div>

        <div class="mt-6 flex flex-wrap gap-3">
          <VButton size="sm" variant="primary" class="!bg-white !text-brand-800 hover:!bg-white/90" @click="$emit('primary')">
            Open control room
          </VButton>
          <VButton
            size="sm"
            variant="secondary"
            class="!border-white/30 !bg-transparent !text-white hover:!bg-white/10"
            @click="$emit('secondary')"
          >
            All elections
          </VButton>
        </div>
      </div>

      <AdminCountdownStrip
        v-if="showCountdown && countdownLabel"
        class="w-full lg:w-[280px]"
        :label="countdownLabel"
        :parts="countdownParts"
      />
    </div>
  </section>
</template>
