<script setup>
import { computed } from "vue";
import { getCandidatePhotoUrl } from "@/utils/candidateDisplay";
import CandidateInfoPanel from "@/components/candidates/CandidateInfoPanel.vue";

const props = defineProps({
  candidate: { type: Object, required: true },
});

const emit = defineEmits(["select"]);

const photoUrl = computed(() => getCandidatePhotoUrl(props.candidate));

function initials(name = "") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}
</script>

<template>
  <div
    role="button"
    tabindex="0"
    class="vb-candidate-card flex h-full min-w-0 cursor-pointer flex-col overflow-hidden rounded-lg border border-border bg-surface text-left shadow-sm transition hover:border-brand-200 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    @click="emit('select', candidate)"
    @keydown.enter.prevent="emit('select', candidate)"
    @keydown.space.prevent="emit('select', candidate)"
  >
    <div class="vb-candidate-photo">
      <img
        v-if="photoUrl"
        :src="photoUrl"
        :alt="`${candidate.full_name} portrait`"
        class="vb-candidate-photo-img"
        loading="lazy"
      />
      <div
        v-else
        class="flex h-full w-full items-center justify-center bg-brand-50 text-lg font-bold text-brand-700"
      >
        {{ initials(candidate.full_name) }}
      </div>
    </div>

    <CandidateInfoPanel
      :candidate="candidate"
      :position-title="candidate.position_title"
    />
  </div>
</template>
