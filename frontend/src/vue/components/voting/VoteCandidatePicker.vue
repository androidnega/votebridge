<script setup>
import { computed, ref } from "vue";
import CandidateCard from "./CandidateCard.vue";

const props = defineProps({
  position: { type: Object, required: true },
  selectedUuids: { type: Array, default: () => [] },
  submitting: { type: Boolean, default: false },
  allowSkip: { type: Boolean, default: true },
  nextLabel: { type: String, default: "Next" },
  backLabel: { type: String, default: "Previous" },
});

const emit = defineEmits(["update:selectedUuids", "confirm", "back"]);

const focusedIndex = ref(0);

const candidates = computed(() => props.position.candidates || []);
const isMulti = computed(() => props.position.choice_type === "multi");
const maxVotes = computed(() => props.position.max_votes_allowed || 1);
const atMax = computed(() => props.selectedUuids.length >= maxVotes.value);
const canConfirm = computed(() => props.allowSkip || props.selectedUuids.length >= 1);

const hint = computed(() => {
  if (isMulti.value) {
    return `Choose up to ${maxVotes.value} candidate${maxVotes.value > 1 ? "s" : ""}, or skip this position.`;
  }
  return "Select a candidate or skip this position if you prefer not to vote here.";
});

function isSelected(uuid) {
  return props.selectedUuids.includes(uuid);
}

function toggleCandidate(uuid) {
  let next = [...props.selectedUuids];
  if (isMulti.value) {
    if (next.includes(uuid)) {
      next = next.filter((id) => id !== uuid);
    } else if (next.length < maxVotes.value) {
      next.push(uuid);
    }
  } else {
    next = next.includes(uuid) ? [] : [uuid];
  }
  emit("update:selectedUuids", next);
}
</script>

<template>
  <section>
    <header class="mb-6">
      <p class="text-xs font-semibold uppercase tracking-wide text-brand-700">Your ballot</p>
      <h2 class="mt-1 text-2xl font-bold text-ink-primary">{{ position.title }}</h2>
      <p v-if="position.description" class="mt-2 text-sm text-ink-secondary">
        {{ position.description }}
      </p>
      <p class="mt-2 text-sm text-ink-secondary">{{ hint }}</p>
    </header>

    <div
      role="listbox"
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
        :choice-type="position.choice_type"
        :tab-index="focusedIndex === index ? 0 : -1"
        variant="student"
        @select="toggleCandidate(candidate.uuid)"
      />
    </div>

    <div class="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
      <button
        type="button"
        class="min-h-[48px] text-sm font-medium text-ink-secondary hover:text-ink-primary"
        :disabled="submitting"
        @click="emit('back')"
      >
        {{ backLabel }}
      </button>
      <button
        type="button"
        class="inline-flex min-h-[48px] items-center justify-center rounded-input bg-brand-700 px-6 text-sm font-semibold text-white transition hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="!canConfirm || submitting"
        @click="emit('confirm')"
      >
        {{ submitting ? "Please wait…" : nextLabel }}
      </button>
    </div>
  </section>
</template>
