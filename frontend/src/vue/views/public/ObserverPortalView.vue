<script setup>
import { computed } from "vue";
import { LoadingSkeleton } from "@/components/ui";
import { branding } from "@/config/branding";
import { useElectionPortal } from "@/composables/useElectionPortal";

const { loading, portal, phaseMeta, countdownParts, latestAnnouncement, formatDate } = useElectionPortal();

const electionTitle = computed(() => portal.value.election?.title || "Campus elections");

const isLive = computed(() => portal.value.phase === "election_open");

const clockText = computed(() => {
  const parts = countdownParts.value;
  if (!parts) return "—";
  if (parts.expired) return "00:00:00";
  return [parts.hours, parts.mins, parts.secs]
    .map((n) => String(n).padStart(2, "0"))
    .join(":");
});
</script>

<template>
  <div class="vb-observer-board">
    <header class="shrink-0 border-b border-border pb-4 text-center">
      <p class="text-[10px] font-medium uppercase tracking-[0.2em] text-slate-400">
        {{ branding.institutionName }}
      </p>
      <h1 class="mt-1 text-lg font-semibold text-slate-900 sm:text-xl">
        {{ electionTitle }}
      </h1>

      <LoadingSkeleton v-if="loading" class="mx-auto mt-3 w-32" variant="list" :rows="1" />

      <p v-else class="vb-observer-phase mt-2.5">
        <span
          class="vb-observer-phase-dot"
          :class="{ 'vb-observer-phase-dot--live': isLive }"
          aria-hidden="true"
        />
        {{ phaseMeta.badge }}
      </p>
    </header>

    <div class="flex min-h-0 flex-1 flex-col items-center justify-center">
      <LoadingSkeleton v-if="loading" variant="list" :rows="2" class="w-full max-w-xs" />

      <template v-else-if="portal.countdown">
        <p class="text-[10px] font-medium uppercase tracking-[0.22em] text-slate-400">
          {{ portal.countdown.label }}
        </p>
        <p class="vb-observer-countdown mt-1">{{ clockText }}</p>
      </template>
    </div>

    <footer class="shrink-0 space-y-4">
      <dl
        v-if="!loading"
        class="grid grid-cols-2 divide-x divide-border border-y border-border py-3 text-center sm:grid-cols-4"
      >
        <div v-if="portal.turnout" class="px-2">
          <dt class="vb-observer-stat-label">Turnout</dt>
          <dd class="mt-0.5 text-base font-semibold tabular-nums text-slate-900">
            {{ portal.turnout.percentage }}%
          </dd>
          <dd class="text-[10px] text-slate-400">
            {{ portal.turnout.participated }}/{{ portal.turnout.eligible }}
          </dd>
        </div>
        <div class="px-2">
          <dt class="vb-observer-stat-label">Status</dt>
          <dd class="mt-0.5 text-sm font-medium capitalize text-slate-800">
            {{ portal.operational_status }}
          </dd>
        </div>
        <div v-if="portal.election?.start_date" class="px-2">
          <dt class="vb-observer-stat-label">Opens</dt>
          <dd class="mt-0.5 text-xs font-medium text-slate-800">{{ formatDate(portal.election.start_date) }}</dd>
        </div>
        <div v-if="portal.election?.end_date" class="px-2">
          <dt class="vb-observer-stat-label">Closes</dt>
          <dd class="mt-0.5 text-xs font-medium text-slate-800">{{ formatDate(portal.election.end_date) }}</dd>
        </div>
      </dl>

      <div v-if="!loading && portal.timeline.length">
        <ol class="flex items-start justify-center">
          <li
            v-for="(step, index) in portal.timeline"
            :key="step.key"
            class="flex flex-1 flex-col items-center"
          >
            <div class="flex w-full items-center">
              <span
                v-if="index > 0"
                class="h-px flex-1"
                :class="step.state === 'pending' ? 'bg-border' : 'bg-slate-300'"
              />
              <span
                class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[9px] font-semibold"
                :class="
                  step.state === 'completed'
                    ? 'bg-slate-800 text-white'
                    : step.state === 'current'
                      ? 'ring-2 ring-slate-800 ring-offset-2 bg-white text-slate-800'
                      : 'border border-border bg-white text-slate-400'
                "
              >
                {{ step.state === 'completed' ? '✓' : '' }}
              </span>
              <span
                v-if="index < portal.timeline.length - 1"
                class="h-px flex-1"
                :class="
                  portal.timeline[index + 1]?.state === 'pending' ? 'bg-border' : 'bg-slate-300'
                "
              />
            </div>
            <span
              class="mt-1.5 max-w-[5rem] truncate text-center text-[10px] leading-tight sm:max-w-none sm:text-[11px]"
              :class="step.state === 'current' ? 'font-medium text-slate-900' : 'text-slate-400'"
            >
              {{ step.label }}
            </span>
          </li>
        </ol>
      </div>

      <p
        v-if="!loading && latestAnnouncement"
        class="truncate text-center text-[11px] text-slate-500"
      >
        {{ latestAnnouncement.title }} — {{ latestAnnouncement.body }}
      </p>

      <p v-else-if="!loading" class="text-center text-[10px] text-slate-400">
        Read-only feed · Results withheld until certification
      </p>
    </footer>
  </div>
</template>
