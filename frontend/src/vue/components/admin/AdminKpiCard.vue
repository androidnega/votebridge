<script setup>
import { computed } from "vue";
import VIcon from "@/components/ui/VIcon.vue";
import { adminKpiHealthStripe } from "@/config/adminWorkspace";

const props = defineProps({
  id: { type: String, default: "" },
  title: { type: String, required: true },
  value: { type: [String, Number], default: "—" },
  detail: { type: String, default: "" },
  hint: { type: String, default: "" },
  healthStatus: { type: String, default: "" },
  clickable: Boolean,
});

defineEmits(["click"]);

const icons = {
  "active-elections": "elections",
  turnout: "analytics",
  positions: "elections",
  candidates: "profile",
  "completed-elections": "results",
  "average-turnout": "analytics",
  published: "results",
  certification: "strongroom",
  "voters-participated": "profile",
  "pending-tasks": "tasks",
  "election-status": "elections",
  "votes-eligible": "analytics",
  "web-votes": "operations",
  "ussd-votes": "operations",
  "active-sessions": "operations",
  "failed-sessions": "security",
  "fraud-alerts": "fraud",
  "security-alerts": "security",
  "system-health": "operations",
};

const accent = computed(() => adminKpiHealthStripe[props.healthStatus] || adminKpiHealthStripe.unknown);
</script>

<template>
  <article
    class="group relative flex min-h-[132px] flex-col overflow-hidden rounded-card border border-border bg-white shadow-card transition-all"
    :class="clickable ? 'cursor-pointer hover:border-slate-300 hover:shadow-md' : ''"
    @click="clickable ? $emit('click') : undefined"
  >
    <span v-if="healthStatus" class="absolute inset-x-0 top-0 h-1" :class="accent" aria-hidden="true" />

    <div class="flex flex-1 flex-col p-5 pt-6">
      <div class="flex items-start justify-between gap-3">
        <p class="text-sm font-medium text-slate-500">{{ title }}</p>
        <span
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-input bg-surface-muted text-slate-500 ring-1 ring-border"
          aria-hidden="true"
        >
          <VIcon :name="icons[id] || 'elections'" size="sm" />
        </span>
      </div>

      <div class="mt-3 flex-1">
        <p class="text-2xl font-semibold tracking-tight text-slate-900">{{ value }}</p>
        <p v-if="detail" class="mt-1 text-sm font-medium text-slate-700">{{ detail }}</p>
      </div>

      <p v-if="hint" class="mt-3 border-t border-border pt-3 text-xs leading-relaxed text-slate-500">
        {{ hint }}
      </p>
    </div>
  </article>
</template>
