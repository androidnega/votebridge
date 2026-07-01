<script setup>
import { computed } from "vue";
import { parseCandidateMeta } from "@/utils/candidateDisplay";
import { VButton } from "@/components/ui";

const props = defineProps({
  candidate: { type: Object, default: null },
});

const emit = defineEmits(["close"]);

const meta = computed(() =>
  props.candidate
    ? parseCandidateMeta(props.candidate.manifesto, props.candidate.department)
    : { faculty: "", department: "", indexNumber: "", manifestoSummary: "" }
);

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
  <Teleport to="body">
    <div
      v-if="candidate"
      class="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/40 p-4 sm:items-center"
      role="dialog"
      aria-modal="true"
      :aria-label="`${candidate.full_name} profile`"
      @click.self="emit('close')"
    >
      <article class="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-card bg-surface p-card shadow-card">
        <div class="flex items-start gap-4">
          <div
            class="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-card bg-brand-50 text-xl font-bold text-brand-700"
          >
            <img
              v-if="candidate.image_url"
              :src="candidate.image_url"
              :alt="`${candidate.full_name} photo`"
              class="h-full w-full object-cover"
            />
            <span v-else>{{ initials(candidate.full_name) }}</span>
          </div>
          <div class="min-w-0 flex-1">
            <h2 class="text-xl font-bold text-slate-900">{{ candidate.full_name }}</h2>
            <p class="mt-1 text-sm font-medium text-brand-700">{{ candidate.position_title }}</p>
            <p v-if="meta.indexNumber" class="mt-1 text-xs text-slate-500">{{ meta.indexNumber }}</p>
          </div>
        </div>

        <dl class="mt-6 space-y-3 text-sm">
          <div v-if="meta.faculty">
            <dt class="font-semibold text-slate-700">Faculty</dt>
            <dd class="text-slate-600">{{ meta.faculty }}</dd>
          </div>
          <div v-if="meta.department">
            <dt class="font-semibold text-slate-700">Department</dt>
            <dd class="text-slate-600">{{ meta.department }}</dd>
          </div>
        </dl>

        <div v-if="candidate.manifesto" class="mt-6">
          <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Manifesto</h3>
          <p class="mt-2 whitespace-pre-line text-sm leading-relaxed text-slate-700">
            {{ candidate.manifesto }}
          </p>
        </div>

        <div class="mt-8">
          <VButton class="min-h-[48px] w-full" variant="secondary" @click="emit('close')">
            Close
          </VButton>
        </div>
      </article>
    </div>
  </Teleport>
</template>
