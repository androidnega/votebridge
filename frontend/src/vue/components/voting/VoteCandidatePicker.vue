<script setup>
import { computed, ref } from "vue";
import { applySelection } from "@/utils/ballotSelection";
import CandidateCard from "./CandidateCard.vue";

const props = defineProps({
  position: { type: Object, required: true },
  selectedUuids: { type: Array, default: () => [] },
  submitting: { type: Boolean, default: false },
  allowSkip: { type: Boolean, default: true },
  nextLabel: { type: String, default: "Next" },
  backLabel: { type: String, default: "Previous" },
  showBack: { type: Boolean, default: true },
  isLastStep: { type: Boolean, default: false },
});

const emit = defineEmits(["update:selectedUuids", "confirm", "back", "skip"]);

const focusedIndex = ref(0);

const candidates = computed(() => props.position.candidates || []);
const isMulti = computed(
  () => props.position.choice_type === "multi" && (props.position.max_votes_allowed || 1) > 1
);
const maxVotes = computed(() => props.position.max_votes_allowed || 1);
const atMax = computed(() => props.selectedUuids.length >= maxVotes.value);
const canProceed = computed(() => props.allowSkip || props.selectedUuids.length >= 1);
const proceedLabel = computed(() =>
  props.isLastStep ? "Review ballot" : props.nextLabel
);

const hint = computed(() => {
  if (isMulti.value) {
    return `Pick up to ${maxVotes.value}, or skip. Tap again to change.`;
  }
  return "Tap a candidate — your latest choice stays selected until you submit.";
});

function isSelected(uuid) {
  return props.selectedUuids.includes(uuid);
}

function selectCandidate(uuid) {
  const next = applySelection(props.position, props.selectedUuids, uuid);
  emit("update:selectedUuids", next);
}

function handleSkip() {
  emit("update:selectedUuids", []);
  emit("skip");
}
</script>

<template>
  <section>
    <header class="mb-5">
      <p class="text-xs font-semibold uppercase tracking-wide text-brand-700">Draft selection</p>
      <h2 class="mt-1 text-xl font-bold text-ink-primary sm:text-2xl">{{ position.title }}</h2>
      <p v-if="position.description" class="mt-1.5 text-sm text-ink-secondary">
        {{ position.description }}
      </p>
      <p class="mt-1.5 text-xs text-ink-secondary">{{ hint }}</p>
    </header>

    <div
      :role="isMulti ? 'listbox' : 'radiogroup'"
      :aria-label="`Candidates for ${position.title}`"
      class="vb-candidate-grid"
    >
      <CandidateCard
        v-for="(candidate, index) in candidates"
        :key="candidate.uuid"
        :candidate="candidate"
        :position-title="position.title"
        :selected="isSelected(candidate.uuid)"
        :disabled="!isSelected(candidate.uuid) && atMax"
        :choice-type="isMulti ? 'multi' : 'single'"
        :tab-index="focusedIndex === index ? 0 : -1"
        variant="student"
        @select="selectCandidate(candidate.uuid)"
      />
    </div>

    <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex flex-wrap gap-3">
        <button
          v-if="showBack"
          type="button"
          class="min-h-[44px] text-sm font-medium text-ink-secondary hover:text-ink-primary"
          :disabled="submitting"
          @click="emit('back')"
        >
          {{ backLabel }}
        </button>
        <button
          v-if="allowSkip"
          type="button"
          class="min-h-[44px] text-sm font-medium text-ink-secondary hover:text-ink-primary"
          :disabled="submitting"
          @click="handleSkip"
        >
          Skip position
        </button>
      </div>
      <button
        type="button"
        class="inline-flex min-h-[44px] items-center justify-center rounded-input bg-brand-700 px-6 text-sm font-semibold text-white transition hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="!canProceed || submitting"
        @click="emit('confirm')"
      >
        {{ submitting ? "Please wait…" : proceedLabel }}
      </button>
    </div>
  </section>
</template>
