<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import { FaIcon, StatusBadge } from "@/components/ui";
import {
  actionButtonClasses,
  electionStatusBadge,
  formatClosingDateParts,
  formatCountdownPill,
  relativeUpdatedLabel,
  resolveCardCountdownTarget,
  resolveElectionAction,
  resolveStudentVotingStatus,
  studentStatusToneClasses,
} from "@/utils/studentActiveElectionDisplay";

const props = defineProps({
  election: { type: Object, required: true },
  actionLoading: { type: Boolean, default: false },
});

const emit = defineEmits(["vote"]);

const router = useRouter();

const countdown = ref(formatCountdownPill(null));
let countdownTimer = null;

const statusBadge = computed(() => electionStatusBadge(props.election.status));
const studentStatus = computed(() => resolveStudentVotingStatus(props.election));
const action = computed(() => resolveElectionAction(props.election));
const closing = computed(() => formatClosingDateParts(props.election.endDate));
const actionClass = computed(() => actionButtonClasses(action.value.tone));

function updateCountdown() {
  countdown.value = formatCountdownPill(resolveCardCountdownTarget(props.election));
}

function runAction() {
  if (props.actionLoading) return;
  if (action.value.handler === "vote") {
    emit("vote", props.election.uuid);
    return;
  }
  if (action.value.route) {
    router.push(action.value.route);
  }
}

function handleCardClick(event) {
  if (event.target.closest("button, a")) return;
  runAction();
}

onMounted(() => {
  updateCountdown();
  countdownTimer = window.setInterval(updateCountdown, 30_000);
});

onUnmounted(() => {
  if (countdownTimer) window.clearInterval(countdownTimer);
});
</script>

<template>
  <article
    class="group flex h-full cursor-pointer flex-col rounded-2xl border border-border bg-surface p-6 shadow-card transition hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-md"
    @click="handleCardClick"
  >
    <header class="flex items-start justify-between gap-3">
      <div class="flex min-w-0 items-start gap-3">
        <div
          class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-700"
          aria-hidden="true"
        >
          <FaIcon icon="fa-box-ballot" :fixed-width="false" class="text-lg" />
        </div>
        <div class="min-w-0">
          <h3 class="text-base font-semibold leading-snug text-ink-primary sm:text-lg">
            {{ election.title }}
          </h3>
          <p class="mt-0.5 text-xs text-ink-secondary">{{ election.electionTypeLabel }}</p>
        </div>
      </div>
      <StatusBadge :status="statusBadge.variant" :label="statusBadge.label" size="sm" />
    </header>

    <div class="mt-5 space-y-4 border-t border-border pt-5">
      <div class="flex gap-3 text-sm">
        <FaIcon icon="fa-calendar-days" class="mt-0.5 shrink-0 text-ink-secondary" />
        <div>
          <p class="text-xs font-medium uppercase tracking-wide text-ink-secondary">Closes</p>
          <p class="font-medium text-ink-primary">{{ closing.dateLine }}</p>
          <p v-if="closing.timeLine" class="text-ink-secondary">{{ closing.timeLine }}</p>
        </div>
      </div>

      <div class="flex gap-3 text-sm">
        <FaIcon icon="fa-users" class="mt-0.5 shrink-0 text-ink-secondary" />
        <div class="min-w-0">
          <p class="text-xs font-medium uppercase tracking-wide text-ink-secondary">Positions</p>
          <ul class="mt-1 space-y-0.5 text-ink-primary">
            <li v-for="title in election.positionPreview" :key="title">{{ title }}</li>
            <li v-if="election.moreCount > 0" class="text-ink-secondary">
              +{{ election.moreCount }} more position{{ election.moreCount === 1 ? "" : "s" }}
            </li>
            <li v-if="!election.positionPreview.length && !election.moreCount" class="text-ink-secondary">
              Positions loading…
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="mt-5">
      <div
        class="inline-flex items-center gap-2 rounded-full bg-surface-muted px-4 py-2.5 text-sm font-semibold text-ink-primary ring-1 ring-border"
        :class="countdown.expired ? 'text-ink-secondary' : ''"
      >
        <FaIcon icon="fa-clock" class="text-brand-700" />
        <span class="text-xs font-medium uppercase tracking-wide text-ink-secondary">Voting ends in</span>
        <span>{{ countdown.label }}</span>
      </div>
    </div>

    <div
      class="mt-4 inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium ring-1 ring-inset"
      :class="studentStatusToneClasses(studentStatus.tone)"
    >
      <span class="h-2 w-2 rounded-full bg-current opacity-80" aria-hidden="true" />
      {{ studentStatus.label }}
    </div>

    <div class="mt-auto pt-5">
      <button
        type="button"
        :class="actionClass"
        :disabled="actionLoading && action.handler === 'vote'"
        @click.stop="runAction"
      >
        <span
          v-if="actionLoading && action.handler === 'vote'"
          class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
          aria-hidden="true"
        />
        {{ action.label }}
      </button>
    </div>

    <footer class="mt-5 grid gap-2 border-t border-border pt-4 text-xs text-ink-secondary sm:grid-cols-3">
      <p class="inline-flex items-center gap-1.5">
        <FaIcon icon="fa-circle-check" class="text-brand-700" />
        <span>Eligible</span>
      </p>
      <p class="inline-flex items-center gap-1.5">
        <FaIcon icon="fa-mobile-screen" class="text-brand-700" />
        <span>{{ election.channels.join(" · ") }}</span>
      </p>
      <p class="inline-flex items-center gap-1.5">
        <FaIcon icon="fa-shield-halved" class="text-brand-700" />
        <span>Protected by SVT</span>
      </p>
    </footer>

    <p class="mt-3 text-[11px] text-ink-secondary">
      Last updated {{ relativeUpdatedLabel(election.lastUpdatedAt) }}
    </p>
  </article>
</template>
