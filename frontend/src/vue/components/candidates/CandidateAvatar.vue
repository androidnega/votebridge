<script setup>
import { computed } from "vue";
import { getCandidatePhotoUrl } from "@/utils/candidateDisplay";

const props = defineProps({
  candidate: { type: Object, required: true },
  size: {
    type: String,
    default: "md",
    validator: (value) => ["sm", "md", "lg"].includes(value),
  },
});

const sizeClasses = {
  sm: "h-10 w-10 text-xs",
  md: "h-12 w-12 text-sm",
  lg: "h-16 w-16 text-base",
};

const photoUrl = computed(() => getCandidatePhotoUrl(props.candidate));

const initials = computed(() =>
  String(props.candidate?.full_name || "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("")
);
</script>

<template>
  <div
    class="shrink-0 overflow-hidden rounded-lg bg-slate-100 ring-1 ring-border"
    :class="sizeClasses[size]"
    aria-hidden="true"
  >
    <img
      v-if="photoUrl"
      :src="photoUrl"
      :alt="`${candidate.full_name} photo`"
      class="h-full w-full object-cover object-[50%_18%]"
    />
    <div
      v-else
      class="flex h-full w-full items-center justify-center bg-brand-50 font-semibold text-brand-700"
    >
      {{ initials || "?" }}
    </div>
  </div>
</template>
