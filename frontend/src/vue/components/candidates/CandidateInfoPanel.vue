<script setup>
import { computed, ref } from "vue";
import { candidateNeedsReadMore, parseCandidateMeta } from "@/utils/candidateDisplay";
import CandidateProfileModal from "./CandidateProfileModal.vue";

const props = defineProps({
  candidate: { type: Object, required: true },
  positionTitle: { type: String, default: "" },
});

const showModal = ref(false);

const meta = computed(() =>
  parseCandidateMeta(props.candidate.manifesto, props.candidate.department)
);

const resolvedPosition = computed(
  () => props.positionTitle || props.candidate.position_title || ""
);

const detailRows = computed(() =>
  [
    { label: "Position", value: resolvedPosition.value },
    { label: "Faculty", value: meta.value.faculty },
    { label: "Department", value: meta.value.department },
    { label: "Academic Level", value: meta.value.academicLevel },
  ].filter((row) => row.value)
);

const showReadMore = computed(() => candidateNeedsReadMore(meta.value));

function openProfile(event) {
  event.preventDefault();
  event.stopPropagation();
  showModal.value = true;
}

function closeProfile() {
  showModal.value = false;
}
</script>

<template>
  <div class="vb-candidate-info">
    <h3 class="truncate text-sm font-bold leading-snug text-ink-primary">
      {{ candidate.full_name }}
    </h3>

    <dl v-if="detailRows.length" class="vb-candidate-info-fields">
      <div v-for="row in detailRows" :key="row.label" class="vb-candidate-info-row">
        <dt>{{ row.label }}</dt>
        <dd class="truncate" :title="row.value">{{ row.value }}</dd>
      </div>
    </dl>

    <div v-if="meta.manifestoSummary" class="vb-candidate-info-manifesto">
      <p class="text-[9px] font-medium text-ink-secondary">Manifesto</p>
      <p class="mt-0.5 line-clamp-2">{{ meta.manifestoSummary }}</p>
    </div>

    <button
      v-if="showReadMore"
      type="button"
      class="vb-candidate-read-more"
      @click="openProfile"
    >
      Read more
    </button>

    <CandidateProfileModal
      v-if="showModal"
      :candidate="candidate"
      :position-title="resolvedPosition"
      @close="closeProfile"
    />
  </div>
</template>
