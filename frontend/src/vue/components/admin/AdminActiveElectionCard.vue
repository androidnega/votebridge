<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { ElectionStatusBadge } from "@/components/voting";
import { VButton } from "@/components/ui";
import { useElectionCountdown, resolveElectionCountdownTarget, resolveCountdownLabel } from "@/composables/useElectionCountdown";

const props = defineProps({
  election: { type: Object, required: true },
  turnout: { type: Number, default: 0 },
  monitorRoute: { type: String, default: null },
});

const router = useRouter();
const status = computed(() => props.election.status || props.election.election_status || "draft");
const title = computed(() => props.election.title || props.election.election_title || "Untitled election");
const countdownTarget = computed(() => resolveElectionCountdownTarget(props.election));
const countdownLabel = computed(() => resolveCountdownLabel(props.election));
const { countdownText } = useElectionCountdown(countdownTarget);

function openControlRoom() {
  if (props.monitorRoute) router.push(props.monitorRoute);
}
</script>

<template>
  <article class="flex flex-col rounded-card border border-[#E5E7EB] bg-white p-5 shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)]">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <h4 class="truncate text-sm font-semibold text-[#1F2937]">{{ title }}</h4>
        <p class="mt-1 text-xs text-[#64748B]">{{ countdownLabel }}: {{ countdownText }}</p>
      </div>
      <ElectionStatusBadge :status="status" size="sm" />
    </div>

    <div class="mt-4">
      <p class="text-xs font-medium uppercase tracking-wide text-[#64748B]">Turnout</p>
      <p class="mt-1 text-3xl font-semibold tabular-nums text-[#1F2937]">{{ Math.min(100, Math.max(0, turnout)) }}%</p>
      <div class="mt-3 h-2 overflow-hidden rounded-full bg-[#F8FAFC]">
        <div
          class="h-full rounded-full bg-[#2563EB] transition-all duration-500"
          :style="{ width: `${Math.min(100, Math.max(0, turnout))}%` }"
        />
      </div>
    </div>

    <VButton
      v-if="monitorRoute"
      class="mt-5 min-h-touch w-full"
      variant="secondary"
      @click="openControlRoom"
    >
      Open Control Room
    </VButton>
  </article>
</template>
