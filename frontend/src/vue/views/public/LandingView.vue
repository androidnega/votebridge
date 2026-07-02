<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";
import { LoadingSkeleton } from "@/components/ui";
import { branding } from "@/config/branding";
import { useElectionPortal } from "@/composables/useElectionPortal";

const { loading, portal, phaseMeta, countdownParts, formatDate } = useElectionPortal();

const isLive = computed(() => portal.value.phase === "election_open");
const isPublished = computed(() => portal.value.phase === "results_published");

const clockText = computed(() => {
  const parts = countdownParts.value;
  if (!parts) return null;
  if (parts.expired) return "00:00:00";
  return [parts.hours, parts.mins, parts.secs]
    .map((n) => String(n).padStart(2, "0"))
    .join(":");
});

const electionTitle = computed(() => portal.value.election?.title || "Campus elections");

const ballotSummary = computed(() => {
  const groups = portal.value.candidates || [];
  const positions = groups.length;
  const nominees = groups.reduce((sum, group) => sum + (group.candidates?.length || 0), 0);
  return { positions, nominees };
});

const heroMessage = computed(() => {
  if (isLive.value) {
    return "Voting is open. Sign in with your index number to cast your ballot securely.";
  }
  if (portal.value.phase === "election_scheduled") {
    return "The next campus election is scheduled. Sign in to confirm your eligibility and get ready.";
  }
  if (isPublished.value) {
    return "Official results are published. Sign in to review outcomes and download your confirmation.";
  }
  return "A secure, transparent platform for student union and faculty elections at TTU.";
});
</script>

<template>
  <div class="vb-landing">
    <header class="vb-landing-nav">
      <div class="flex min-w-0 items-center gap-3">
        <img
          v-if="branding.institutionLogoUrl"
          :src="branding.institutionLogoUrl"
          alt=""
          class="h-10 w-10 shrink-0 object-contain sm:h-11 sm:w-11"
          aria-hidden="true"
        />
        <div class="min-w-0 text-left">
          <p class="truncate text-[11px] font-medium uppercase tracking-[0.16em] text-slate-500">
            {{ branding.institutionName }}
          </p>
          <p class="truncate text-sm font-semibold text-slate-900 sm:text-base">{{ branding.systemName }}</p>
        </div>
      </div>
      <RouterLink to="/auth/login" class="vb-landing-nav-signin">Sign in</RouterLink>
    </header>

    <section class="vb-landing-hero">
      <div class="vb-landing-hero-grid">
        <div class="min-w-0">
          <p class="vb-landing-eyebrow">{{ branding.tagline }}</p>
          <h1 class="vb-landing-title">Campus elections, built for trust</h1>
          <p class="vb-landing-lead">{{ heroMessage }}</p>

          <dl v-if="!loading && portal.election" class="mt-8 grid grid-cols-3 gap-3 sm:max-w-md">
            <div class="vb-landing-mini-stat">
              <dt class="vb-landing-mini-stat-label">Positions</dt>
              <dd class="vb-landing-mini-stat-value">{{ ballotSummary.positions || "—" }}</dd>
            </div>
            <div class="vb-landing-mini-stat">
              <dt class="vb-landing-mini-stat-label">Candidates</dt>
              <dd class="vb-landing-mini-stat-value">{{ ballotSummary.nominees || "—" }}</dd>
            </div>
            <div class="vb-landing-mini-stat">
              <dt class="vb-landing-mini-stat-label">Phase</dt>
              <dd class="vb-landing-mini-stat-value text-sm capitalize">{{ phaseMeta.badge }}</dd>
            </div>
          </dl>
        </div>

        <aside class="vb-landing-spotlight">
          <LoadingSkeleton v-if="loading" variant="card" />

          <template v-else>
            <p class="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">Live election board</p>
            <h2 class="mt-2 text-lg font-semibold text-slate-900 sm:text-xl">{{ electionTitle }}</h2>

            <p class="vb-public-status mt-4">
              <span
                class="vb-public-status-dot"
                :class="{ 'vb-public-status-dot--live': isLive }"
                aria-hidden="true"
              />
              {{ phaseMeta.badge }}
            </p>

            <div v-if="portal.countdown && clockText" class="vb-landing-countdown mt-5 px-4 py-4 text-center">
              <p class="text-[10px] font-medium uppercase tracking-[0.16em] text-brand-100">
                {{ portal.countdown.label }}
              </p>
              <p class="vb-landing-countdown-time mt-1">{{ clockText }}</p>
            </div>

            <dl class="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div class="rounded-lg border border-border bg-white px-3 py-2.5">
                <dt class="text-xs text-slate-500">Operations</dt>
                <dd class="mt-0.5 font-medium capitalize text-slate-800">{{ portal.operational_status }}</dd>
              </div>
              <div v-if="portal.election?.start_date" class="rounded-lg border border-border bg-white px-3 py-2.5">
                <dt class="text-xs text-slate-500">Opens</dt>
                <dd class="mt-0.5 text-xs font-medium text-slate-800">{{ formatDate(portal.election.start_date) }}</dd>
              </div>
              <div v-if="portal.election?.end_date" class="rounded-lg border border-border bg-white px-3 py-2.5">
                <dt class="text-xs text-slate-500">Closes</dt>
                <dd class="mt-0.5 text-xs font-medium text-slate-800">{{ formatDate(portal.election.end_date) }}</dd>
              </div>
            </dl>
          </template>
        </aside>
      </div>
    </section>
  </div>
</template>
