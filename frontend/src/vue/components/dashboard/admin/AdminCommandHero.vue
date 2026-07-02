<script setup>
import { StatusBadge, VButton } from "@/components/ui";
import AdminCountdownStrip from "./AdminCountdownStrip.vue";

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  institution: { type: String, default: "" },
  imageUrl: { type: String, default: "" },
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
    class="relative flex h-full min-h-0 flex-col overflow-hidden rounded-card border border-border bg-brand-800 shadow-[0_8px_30px_-12px_rgb(15_23_42_/_0.18)]"
  >
    <div
      v-if="imageUrl"
      class="pointer-events-none absolute inset-0 scale-[1.03] bg-cover bg-center"
      :style="{ backgroundImage: `url(${imageUrl})` }"
      aria-hidden="true"
    />
    <div class="pointer-events-none absolute inset-0 bg-brand-900/15" aria-hidden="true" />

    <div
      class="relative z-10 grid flex-1 gap-4 p-4 sm:gap-5 sm:p-5 lg:grid-cols-[minmax(0,1fr)_minmax(220px,280px)] lg:items-center lg:gap-6 lg:p-6"
    >
      <div class="min-w-0 text-white">
        <p v-if="institution" class="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/75 sm:text-xs">
          {{ institution }}
        </p>
        <h1 class="mt-1.5 text-xl font-bold tracking-tight sm:text-2xl lg:text-[1.75rem] lg:leading-tight">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="mt-1.5 max-w-2xl text-sm leading-snug text-white/85">
          {{ subtitle }}
        </p>

        <div class="mt-3 flex flex-wrap items-center gap-2">
          <StatusBadge v-if="statusLabel" :status="status" :label="statusLabel" />
          <span
            v-if="isLive"
            class="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-2.5 py-0.5 text-[11px] font-semibold text-white"
          >
            <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-300" aria-hidden="true" />
            Live
          </span>
        </div>

        <div class="mt-4 flex flex-wrap gap-2.5">
          <VButton
            size="sm"
            variant="primary"
            class="!bg-white !text-brand-800 hover:!bg-white/90"
            @click="$emit('primary')"
          >
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
        class="w-full shrink-0"
        :label="countdownLabel"
        :parts="countdownParts"
      />
    </div>
  </section>
</template>
