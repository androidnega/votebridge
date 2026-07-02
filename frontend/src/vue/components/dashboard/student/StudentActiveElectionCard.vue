<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { FaIcon, StatusBadge } from "@/components/ui";
import { useElectionCountdown } from "@/composables/useElectionCountdown";
import {
  actionButtonClasses,
  electionStatusBadge,
  resolveCardCountdownTarget,
  resolveElectionAction,
  resolveStudentVotingStatus,
} from "@/utils/studentActiveElectionDisplay";

const props = defineProps({
  election: { type: Object, required: true },
  isEntering: { type: Boolean, default: false },
});

const emit = defineEmits(["vote"]);

const router = useRouter();

const statusBadge = computed(() => electionStatusBadge(props.election.status));
const studentStatus = computed(() => resolveStudentVotingStatus(props.election));
const action = computed(() => resolveElectionAction(props.election));
const actionClass = computed(() => {
  const tone = action.value.handler === "vote" ? "primary" : action.value.tone;
  return actionButtonClasses(tone).replace(" w-full", "");
});
const isSubmitted = computed(() => props.election.hasVoted);

const countdownTarget = computed(() => resolveCardCountdownTarget(props.election));
const { countdownText } = useElectionCountdown(countdownTarget);

const positionSummary = computed(() => {
  const count = props.election.positionCount;
  if (count > 0) return `${count} position${count === 1 ? "" : "s"}`;
  const preview = props.election.positionPreview?.length || 0;
  const more = props.election.moreCount || 0;
  const total = preview + more;
  if (total > 0) return `${total} position${total === 1 ? "" : "s"}`;
  return "";
});

const statusTextClass = computed(() => {
  const map = {
    green: "text-success-700",
    orange: "text-warning-700",
    blue: "text-info-700",
    red: "text-danger-700",
  };
  return map[studentStatus.value.tone] || map.green;
});

function runAction() {
  if (props.isEntering) return;
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
</script>

<template>
  <article
    v-if="isSubmitted"
    class="flex w-full cursor-pointer items-center gap-3 rounded-lg border border-success-100 bg-success-50 px-4 py-3 transition hover:border-success-200"
    @click="handleCardClick"
  >
    <FaIcon icon="fa-circle-check" class="shrink-0 text-success-600" />
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-semibold text-ink-primary">{{ election.title }}</p>
      <p class="text-xs text-success-700">Vote recorded</p>
    </div>
    <button
      type="button"
      class="shrink-0 text-xs font-semibold text-brand-700 hover:text-brand-hover"
      @click.stop="runAction"
    >
      Receipt
    </button>
  </article>

  <article
    v-else
    class="w-full cursor-pointer overflow-hidden rounded-lg border border-border bg-surface transition"
    :class="
      isEntering
        ? 'border-brand-300 ring-2 ring-brand-100'
        : 'hover:border-brand-200'
    "
    @click="handleCardClick"
  >
    <div class="px-4 py-3">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0 flex-1">
          <h3 class="text-sm font-semibold leading-snug text-ink-primary sm:text-base">
            {{ election.title }}
          </h3>
          <p class="mt-0.5 text-xs font-semibold" :class="statusTextClass">
            {{ studentStatus.label }}
          </p>
          <p v-if="positionSummary" class="mt-0.5 text-xs text-ink-secondary">
            {{ positionSummary }}
          </p>
        </div>
        <StatusBadge :status="statusBadge.variant" :label="statusBadge.label" size="sm" />
      </div>
    </div>

    <div class="flex items-center justify-between gap-4 border-t border-border px-4 py-3">
      <div class="min-w-0">
        <p class="text-[10px] font-medium uppercase tracking-wide text-ink-secondary">Ends in</p>
        <p
          class="mt-0.5 text-xl font-bold tabular-nums leading-none text-brand-700 sm:text-2xl"
          aria-live="polite"
        >
          {{ countdownText }}
        </p>
      </div>

      <button
        type="button"
        class="shrink-0 px-4"
        :class="actionClass"
        :disabled="isEntering && action.handler === 'vote'"
        @click.stop="runAction"
      >
        <span
          v-if="isEntering && action.handler === 'vote'"
          class="mr-1.5 inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white"
          aria-hidden="true"
        />
        {{ action.label }}
      </button>
    </div>
  </article>
</template>
