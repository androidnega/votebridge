<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { StatusBadge, VButton } from "@/components/ui";
import { electionHealth } from "@/config/designTokens";
import {
  resolveCountdownLabel,
  resolveElectionCountdownTarget,
  useElectionCountdown,
} from "@/composables/useElectionCountdown";

const props = defineProps({
  election: {
    type: Object,
    default: null,
  },
  turnoutPercentage: {
    type: Number,
    default: null,
  },
  healthLevel: {
    type: String,
    default: "healthy",
    validator: (value) => ["healthy", "attention", "critical"].includes(value),
  },
  nextAction: {
    type: Object,
    default: null,
  },
  compact: Boolean,
});

const router = useRouter();

const status = computed(
  () => props.election?.status || props.election?.election_status || "draft"
);
const title = computed(
  () => props.election?.title || props.election?.election_title || "No active election"
);
const countdownTarget = computed(() => resolveElectionCountdownTarget(props.election));
const countdownLabel = computed(() => resolveCountdownLabel(props.election));
const { countdownText } = useElectionCountdown(countdownTarget);

const healthMeta = computed(() => electionHealth[props.healthLevel] || electionHealth.healthy);

const workspaceRoute = computed(() => {
  const uuid = props.election?.uuid || props.election?.election_uuid;
  return uuid ? `/dashboard/elections/${uuid}` : "/dashboard/elections";
});
</script>

<template>
  <section class="vb-election-hero" aria-labelledby="election-context-title">
    <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
      <div class="min-w-0 flex-1">
        <p class="vb-vault-caption !text-brand-200">Active election</p>
        <div class="mt-2 flex flex-wrap items-center gap-3">
          <StatusBadge :status="status" :size="compact ? 'md' : 'lg'" />
          <span
            class="vb-status-pill ring-1 ring-inset"
            :class="healthMeta.class"
          >
            {{ healthMeta.label }}
          </span>
        </div>
        <h2 id="election-context-title" class="mt-3 text-2xl font-bold">
          {{ title }}
        </h2>
        <p v-if="turnoutPercentage !== null" class="mt-2 text-sm vb-election-hero-muted">
          Turnout {{ turnoutPercentage }}%
        </p>
      </div>

      <div class="flex flex-col gap-3 sm:items-end">
        <div
          v-if="countdownTarget"
          class="rounded-input border border-white/15 bg-white/10 px-4 py-3 text-left sm:min-w-[180px] sm:text-right"
        >
          <p class="text-xs uppercase tracking-wide text-brand-200">{{ countdownLabel }}</p>
          <p class="mt-1 text-2xl font-bold tabular-nums">{{ countdownText }}</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <VButton
            v-if="nextAction"
            size="sm"
            class="!border-white/20 !bg-white !text-brand-700 hover:!bg-brand-50"
            @click="router.push(nextAction.route)"
          >
            {{ nextAction.label }}
          </VButton>
          <VButton
            v-if="election"
            size="sm"
            variant="secondary"
            class="border-white/20 bg-white/10 text-white hover:bg-white/20"
            @click="router.push(workspaceRoute)"
          >
            Open workspace
          </VButton>
        </div>
      </div>
    </div>
  </section>
</template>
