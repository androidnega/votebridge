<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { publicApi } from "@/api/public";

const props = defineProps({
  compact: { type: Boolean, default: false },
});

const loading = ref(true);
const portal = ref({
  phase: "before_election",
  election: null,
  countdown: null,
  turnout: null,
  timeline: [],
  candidates: [],
  announcements: [],
  operational_status: "standby",
});

const countdownText = ref("—");
let countdownTimer = null;

const phaseLabels = {
  before_election: { badge: "Standby", class: "bg-slate-700 text-slate-200" },
  election_scheduled: { badge: "Scheduled", class: "bg-info-50 text-info-700 ring-info-200" },
  election_open: { badge: "Voting open", class: "bg-success-50 text-success-700 ring-success-200" },
  awaiting_certification: { badge: "Awaiting certification", class: "bg-warning-50 text-warning-700 ring-warning-200" },
  results_published: { badge: "Results published", class: "bg-brand-50 text-brand-700 ring-brand-200" },
};

const phaseMeta = computed(() => phaseLabels[portal.value.phase] || phaseLabels.before_election);

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function updateCountdown() {
  const target = portal.value.countdown?.target_at;
  if (!target) {
    countdownText.value = "—";
    return;
  }
  const diff = new Date(target).getTime() - Date.now();
  if (diff <= 0) {
    countdownText.value = "Now";
    return;
  }
  const hours = Math.floor(diff / 3_600_000);
  const mins = Math.floor((diff % 3_600_000) / 60_000);
  const secs = Math.floor((diff % 60_000) / 1000);
  countdownText.value = `${hours}h ${mins}m ${secs}s`;
}

onMounted(async () => {
  try {
    portal.value = await publicApi.getElectionPortal();
  } catch {
    /* defaults */
  } finally {
    loading.value = false;
    updateCountdown();
    countdownTimer = setInterval(updateCountdown, 1000);
  }
});

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer);
});
</script>

<template>
  <div class="space-y-section">
    <section class="rounded-card border border-border bg-surface p-card shadow-sm">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Current election phase</p>
          <h2 class="mt-1 text-xl font-semibold text-slate-900">
            {{ portal.election?.title || "Campus elections" }}
          </h2>
        </div>
        <span
          class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset"
          :class="phaseMeta.class"
        >
          {{ phaseMeta.badge }}
        </span>
      </div>

      <div v-if="loading" class="mt-4 space-y-2">
        <div class="h-4 w-2/3 animate-pulse rounded bg-slate-200" />
        <div class="h-4 w-1/2 animate-pulse rounded bg-slate-200" />
      </div>
      <template v-else>
        <div v-if="portal.countdown" class="mt-4 rounded-input border border-border bg-surface-muted p-4">
          <p class="text-xs uppercase tracking-wide text-slate-500">{{ portal.countdown.label }}</p>
          <p class="mt-1 text-3xl font-bold tabular-nums text-brand-700">{{ countdownText }}</p>
        </div>

        <dl v-if="portal.election" class="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <div v-if="portal.turnout">
            <dt class="text-slate-500">Participation</dt>
            <dd class="font-medium text-slate-800">
              {{ portal.turnout.percentage }}% ({{ portal.turnout.participated }} of
              {{ portal.turnout.eligible }} eligible)
            </dd>
          </div>
          <div>
            <dt class="text-slate-500">Operational status</dt>
            <dd class="font-medium capitalize text-slate-800">{{ portal.operational_status }}</dd>
          </div>
          <div v-if="portal.election.start_date">
            <dt class="text-slate-500">Opens</dt>
            <dd class="font-medium text-slate-800">{{ formatDate(portal.election.start_date) }}</dd>
          </div>
          <div v-if="portal.election.end_date">
            <dt class="text-slate-500">Closes</dt>
            <dd class="font-medium text-slate-800">{{ formatDate(portal.election.end_date) }}</dd>
          </div>
        </dl>
      </template>
    </section>

    <section v-if="!loading && portal.timeline.length" class="rounded-card border border-border bg-surface p-card shadow-sm">
      <h3 class="text-lg font-semibold text-slate-900">Election timeline</h3>
      <ol class="mt-4 space-y-3">
        <li
          v-for="step in portal.timeline"
          :key="step.key"
          class="flex gap-3 rounded-input border border-border p-3"
          :class="step.state === 'current' ? 'border-brand-600 bg-brand-50/40' : ''"
        >
          <span
            class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold"
            :class="
              step.state === 'completed'
                ? 'bg-success-50 text-success-700'
                : step.state === 'current'
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-100 text-slate-500'
            "
          >
            {{ step.state === 'completed' ? '✓' : '•' }}
          </span>
          <div>
            <p class="font-medium text-slate-800">{{ step.label }}</p>
            <p v-if="step.at" class="text-xs text-slate-500">{{ formatDate(step.at) }}</p>
            <p v-else-if="step.state === 'current'" class="text-xs text-brand-700">In progress</p>
          </div>
        </li>
      </ol>
    </section>

    <section
      v-if="!loading && portal.announcements.length"
      class="rounded-card border border-border bg-surface p-card shadow-sm"
    >
      <h3 class="text-lg font-semibold text-slate-900">Public announcements</h3>
      <ul class="mt-4 space-y-3">
        <li
          v-for="(item, idx) in portal.announcements"
          :key="idx"
          class="rounded-input border border-border p-4"
        >
          <p class="font-medium text-slate-800">{{ item.title }}</p>
          <p class="mt-1 text-sm text-slate-600">{{ item.body }}</p>
          <p class="mt-2 text-xs text-slate-500">{{ formatDate(item.at) }}</p>
        </li>
      </ul>
    </section>

    <section
      v-if="!loading && portal.candidates.length && !compact"
      class="rounded-card border border-border bg-surface p-card shadow-sm"
    >
      <h3 class="text-lg font-semibold text-slate-900">Candidates</h3>
      <p class="mt-1 text-sm text-slate-500">Approved candidates — vote totals are hidden while voting is open.</p>
      <div class="mt-4 space-y-6">
        <div v-for="group in portal.candidates" :key="group.position_uuid">
          <h4 class="font-medium text-slate-800">{{ group.position_title }}</h4>
          <ul class="mt-2 grid gap-3 sm:grid-cols-2">
            <li
              v-for="candidate in group.candidates"
              :key="candidate.uuid"
              class="rounded-input border border-border p-4"
            >
              <p class="font-medium text-slate-900">{{ candidate.full_name }}</p>
              <p v-if="candidate.department" class="text-xs text-slate-500">{{ candidate.department }}</p>
              <p v-if="candidate.manifesto_excerpt" class="mt-2 text-sm text-slate-600">
                {{ candidate.manifesto_excerpt }}
              </p>
            </li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>
