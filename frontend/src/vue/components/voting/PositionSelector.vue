<script setup>
import { computed, ref } from "vue";
import CandidateCard from "./CandidateCard.vue";

const props = defineProps({
  position: {
    type: Object,
    required: true,
  },
  selectedUuids: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:selectedUuids"]);

const focusedIndex = ref(0);

const candidates = computed(() => props.position.candidates || []);
const isMulti = computed(() => props.position.choice_type === "multi");
const maxVotes = computed(() => props.position.max_votes_allowed || 1);
const atMax = computed(() => props.selectedUuids.length >= maxVotes.value);

const hint = computed(() => {
  if (isMulti.value) {
    return `Select up to ${maxVotes.value} candidate${maxVotes.value > 1 ? "s" : ""}.`;
  }
  return "Select one candidate.";
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
    next = [uuid];
  }
  emit("update:selectedUuids", next);
}

function onKeydown(event, index) {
  const last = candidates.value.length - 1;
  if (event.key === "ArrowDown" || event.key === "ArrowRight") {
    event.preventDefault();
    focusedIndex.value = Math.min(last, index + 1);
  } else if (event.key === "ArrowUp" || event.key === "ArrowLeft") {
    event.preventDefault();
    focusedIndex.value = Math.max(0, index - 1);
  } else if (event.key === " " || event.key === "Enter") {
    event.preventDefault();
    toggleCandidate(candidates.value[index].uuid);
  }
}
</script>

<template>
  <section>
    <header class="mb-4">
      <h3 class="text-lg font-semibold text-slate-900">{{ position.title }}</h3>
      <p v-if="position.description" class="mt-1 text-sm text-slate-600">{{ position.description }}</p>
      <p class="mt-2 text-xs text-slate-500">{{ hint }}</p>
      <p v-if="isMulti" class="mt-1 text-xs font-medium text-brand-700">
        {{ selectedUuids.length }} / {{ maxVotes }} selected
      </p>
    </header>

    <div
      role="listbox"
      :aria-label="`Candidates for ${position.title}`"
      :aria-multiselectable="isMulti"
      class="grid grid-cols-1 gap-3 sm:grid-cols-2"
    >
      <CandidateCard
        v-for="(candidate, index) in candidates"
        :key="candidate.uuid"
        :candidate="candidate"
        :selected="isSelected(candidate.uuid)"
        :disabled="!isSelected(candidate.uuid) && atMax"
        :choice-type="position.choice_type"
        :tab-index="focusedIndex === index ? 0 : -1"
        @select="toggleCandidate(candidate.uuid)"
        @keydown="onKeydown($event, index)"
      />
    </div>
  </section>
</template>
