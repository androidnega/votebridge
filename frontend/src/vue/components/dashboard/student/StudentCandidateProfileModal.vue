<script setup>
import CandidateProfileModal from "@/components/candidates/CandidateProfileModal.vue";

defineProps({
  candidate: { type: Object, default: null },
  positionTitle: { type: String, default: "" },
});

defineEmits(["close"]);
</script>

<template>
  <CandidateProfileModal
    :candidate="candidate"
    :position-title="positionTitle"
    @close="$emit('close')"
  />
</template>
