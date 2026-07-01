<script setup>
import { computed } from "vue";
import { getCandidatePhotoUrl, parseCandidateMeta } from "@/utils/candidateDisplay";
import { VButton } from "@/components/ui";

const props = defineProps({
  candidate: { type: Object, default: null },
  positionTitle: { type: String, default: "" },
});

const emit = defineEmits(["close"]);

const photoUrl = computed(() => (props.candidate ? getCandidatePhotoUrl(props.candidate) : null));

const meta = computed(() =>
  props.candidate
    ? parseCandidateMeta(props.candidate.manifesto, props.candidate.department)
    : {
        faculty: "",
        department: "",
        academicLevel: "",
        indexNumber: "",
        manifestoText: "",
        manifestoSummary: "",
      }
);

const resolvedPosition = computed(
  () => props.positionTitle || props.candidate?.position_title || "—"
);

const profileRows = computed(() => {
  if (!props.candidate) return [];
  return [
    { label: "Full Name", value: props.candidate.full_name },
    { label: "Position", value: resolvedPosition.value },
    { label: "Faculty", value: meta.value.faculty },
    { label: "Department", value: meta.value.department },
    { label: "Academic Level", value: meta.value.academicLevel },
  ].filter((row) => row.value);
});

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
      <article class="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-card bg-surface p-card shadow-card">
        <div class="flex items-start gap-4">
          <div
            class="aspect-square h-24 w-24 shrink-0 overflow-hidden rounded-lg bg-slate-100 sm:h-28 sm:w-28"
          >
            <img
              v-if="photoUrl"
              :src="photoUrl"
              :alt="`${candidate.full_name} photo`"
              class="h-full w-full object-cover object-[50%_18%]"
            />
            <div
              v-else
              class="flex h-full w-full items-center justify-center bg-brand-50 text-xl font-bold text-brand-700"
            >
              {{ initials(candidate.full_name) }}
            </div>
          </div>
          <div class="min-w-0 flex-1">
            <h2 class="text-lg font-bold text-ink-primary">{{ candidate.full_name }}</h2>
            <p class="mt-1 text-sm font-medium text-brand-700">{{ resolvedPosition }}</p>
            <p v-if="meta.indexNumber" class="mt-1 text-xs text-ink-secondary">
              {{ meta.indexNumber }}
            </p>
          </div>
        </div>

        <dl class="mt-5 space-y-2.5 border-t border-border pt-4 text-sm">
          <div v-for="row in profileRows" :key="row.label" class="grid grid-cols-[7.5rem_1fr] gap-2">
            <dt class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">
              {{ row.label }}
            </dt>
            <dd class="text-sm text-ink-primary">{{ row.value }}</dd>
          </div>
        </dl>

        <div v-if="meta.manifestoText" class="mt-5 border-t border-border pt-4">
          <h3 class="text-xs font-semibold uppercase tracking-wide text-ink-secondary">Manifesto</h3>
          <p class="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-primary">
            {{ meta.manifestoText }}
          </p>
        </div>

        <div class="mt-6">
          <VButton class="min-h-[48px] w-full" variant="secondary" @click="emit('close')">
            Close
          </VButton>
        </div>
      </article>
    </div>
  </Teleport>
</template>
