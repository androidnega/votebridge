<script setup>
import { useElectionPortal } from "@/composables/useElectionPortal";
import { LoadingSkeleton } from "@/components/ui";

const props = defineProps({
  compact: { type: Boolean, default: false },
});

const { loading, portal, phaseMeta, countdownText, formatDate } = useElectionPortal();
</script>

<template>
  <div class="space-y-section">
    <section class="vb-surface-panel">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="vb-caption">Current election</p>
          <h2 class="mt-0.5 text-lg font-semibold text-slate-900">
            {{ portal.election?.title || "Campus elections" }}
          </h2>
        </div>
        <span class="vb-status-pill" :class="phaseMeta.class">
          {{ phaseMeta.badge }}
        </span>
      </div>

      <LoadingSkeleton v-if="loading" class="mt-4" variant="list" :rows="2" />
      <template v-else>
        <div
          v-if="portal.countdown"
          class="mt-4 flex items-baseline justify-between gap-4 rounded-input bg-surface-muted px-4 py-3"
        >
          <p class="text-sm text-slate-600">{{ portal.countdown.label }}</p>
          <p class="text-xl font-semibold tabular-nums text-brand-700">{{ countdownText }}</p>
        </div>

        <dl v-if="portal.election" class="mt-4 grid gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
          <div v-if="portal.turnout">
            <dt class="text-slate-500">Participation</dt>
            <dd class="font-medium text-slate-800">
              {{ portal.turnout.percentage }}% ({{ portal.turnout.participated }} of
              {{ portal.turnout.eligible }} eligible)
            </dd>
          </div>
          <div>
            <dt class="text-slate-500">Status</dt>
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

    <section v-if="!loading && portal.timeline.length" class="vb-surface-panel">
      <h3 class="vb-section-title">Timeline</h3>
      <ol class="vb-divider-list mt-3">
        <li
          v-for="step in portal.timeline"
          :key="step.key"
          class="flex gap-3 py-3 first:pt-0 last:pb-0"
        >
          <span
            class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-bold"
            :class="
              step.state === 'completed'
                ? 'bg-success-50 text-success-700'
                : step.state === 'current'
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-100 text-slate-400'
            "
          >
            {{ step.state === 'completed' ? '✓' : '' }}
          </span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium" :class="step.state === 'current' ? 'text-brand-700' : 'text-slate-800'">
              {{ step.label }}
            </p>
            <p v-if="step.at" class="text-xs text-slate-500">{{ formatDate(step.at) }}</p>
            <p v-else-if="step.state === 'current'" class="text-xs text-brand-600">In progress</p>
          </div>
        </li>
      </ol>
    </section>

    <section v-if="!loading && portal.announcements.length" class="vb-surface-panel">
      <h3 class="vb-section-title">Announcements</h3>
      <ul class="vb-divider-list mt-3">
        <li v-for="(item, idx) in portal.announcements" :key="idx" class="py-3 first:pt-0 last:pb-0">
          <p class="text-sm font-medium text-slate-800">{{ item.title }}</p>
          <p class="mt-0.5 text-sm text-slate-600">{{ item.body }}</p>
          <p class="mt-1 text-xs text-slate-500">{{ formatDate(item.at) }}</p>
        </li>
      </ul>
    </section>

    <section v-if="!loading && portal.candidates.length && !compact" class="vb-surface-panel">
      <h3 class="vb-section-title">Candidates</h3>
      <p class="mt-1 text-sm text-slate-500">Approved candidates — vote totals hidden while voting is open.</p>
      <div class="mt-4 space-y-5">
        <div v-for="group in portal.candidates" :key="group.position_uuid">
          <h4 class="text-sm font-medium text-slate-800">{{ group.position_title }}</h4>
          <ul class="mt-2 grid gap-2 sm:grid-cols-2">
            <li
              v-for="candidate in group.candidates"
              :key="candidate.uuid"
              class="rounded-input bg-surface-muted px-3 py-2.5"
            >
              <p class="text-sm font-medium text-slate-900">{{ candidate.full_name }}</p>
              <p v-if="candidate.department" class="text-xs text-slate-500">{{ candidate.department }}</p>
              <p v-if="candidate.manifesto_excerpt" class="mt-1 text-xs text-slate-600">
                {{ candidate.manifesto_excerpt }}
              </p>
            </li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>
