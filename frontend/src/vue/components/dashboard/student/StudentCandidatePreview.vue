<script setup>
import StudentCandidateCard from "./StudentCandidateCard.vue";

defineProps({
  groups: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["select-candidate"]);
</script>

<template>
  <section aria-labelledby="student-candidates-heading">
    <div class="mb-4">
      <h2 id="student-candidates-heading" class="text-lg font-semibold text-slate-900">
        Candidates
      </h2>
      <p class="mt-1 text-sm text-slate-600">
        Review who is contesting each position before you vote.
      </p>
    </div>

    <p v-if="loading" class="text-sm text-slate-500">Loading candidates…</p>

    <div v-else-if="groups.length" class="space-y-8">
      <div v-for="group in groups" :key="group.positionUuid || group.positionTitle">
        <h3 class="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          {{ group.positionTitle }}
        </h3>
        <div class="vb-candidate-grid">
          <StudentCandidateCard
            v-for="candidate in group.candidates"
            :key="candidate.uuid"
            :candidate="candidate"
            @select="emit('select-candidate', $event)"
          />
        </div>
      </div>
    </div>

    <p v-else class="rounded-card border border-dashed border-border bg-surface-muted px-4 py-6 text-sm text-slate-600">
      Candidate profiles will appear here when nominations are published.
    </p>
  </section>
</template>
