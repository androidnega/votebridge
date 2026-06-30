<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";
import PublicBrandHeader from "@/components/public/PublicBrandHeader.vue";
import { LoadingSkeleton } from "@/components/ui";
import { useElectionPortal } from "@/composables/useElectionPortal";

const { loading, portal, phaseMeta, countdownParts } = useElectionPortal();

const isLive = computed(() => portal.value.phase === "election_open");

const clockText = computed(() => {
  const parts = countdownParts.value;
  if (!parts) return null;
  if (parts.expired) return "00:00:00";
  return [parts.hours, parts.mins, parts.secs]
    .map((n) => String(n).padStart(2, "0"))
    .join(":");
});

const electionTitle = computed(() => portal.value.election?.title || "Campus elections");
</script>

<template>
  <div class="vb-public-card">
    <PublicBrandHeader />

    <div class="border-t border-border pt-6 text-center">
      <LoadingSkeleton v-if="loading" class="mx-auto max-w-xs" variant="list" :rows="2" />

      <template v-else>
        <p class="text-[10px] font-medium uppercase tracking-[0.2em] text-slate-400">Current election</p>
        <p class="mt-1 text-base font-semibold text-slate-900">{{ electionTitle }}</p>

        <p class="vb-public-status mt-3">
          <span
            class="vb-public-status-dot"
            :class="{ 'vb-public-status-dot--live': isLive }"
            aria-hidden="true"
          />
          {{ phaseMeta.badge }}
        </p>

        <div v-if="portal.countdown && clockText" class="mt-5">
          <p class="text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">
            {{ portal.countdown.label }}
          </p>
          <p class="vb-public-countdown mt-1">{{ clockText }}</p>
        </div>
      </template>
    </div>

    <div class="mt-8 border-t border-border pt-6">
      <RouterLink to="/auth/login" class="vb-public-primary-btn">Sign in to vote</RouterLink>
    </div>
  </div>
</template>
