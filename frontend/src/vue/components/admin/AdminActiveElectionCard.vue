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

const clampedTurnout = computed(() => Math.min(100, Math.max(0, props.turnout)));

function openControlRoom() {
  if (props.monitorRoute) router.push(props.monitorRoute);
}
</script>

<template>
  <article
    class="flex w-full min-w-0 flex-col gap-4 rounded-card border border-[#E5E7EB] bg-white p-4 shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)] sm:flex-row sm:items-center sm:gap-6 sm:p-5"
  >
    <div class="min-w-0 flex-1">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div class="min-w-0 flex-1">
          <h4 class="text-base font-semibold leading-snug text-[#1F2937]">{{ title }}</h4>
          <p class="mt-1 text-sm text-[#64748B]">{{ countdownLabel }}: {{ countdownText }}</p>
        </div>
        <ElectionStatusBadge :status="status" size="sm" />
      </div>
    </div>

    <div class="w-full min-w-0 sm:max-w-[14rem] sm:flex-shrink-0">
      <p class="text-xs font-medium uppercase tracking-wide text-[#64748B]">Turnout</p>
      <p class="mt-1 text-2xl font-semibold tabular-nums text-[#1F2937] sm:text-3xl">{{ clampedTurnout }}%</p>
      <div class="mt-2 h-2 overflow-hidden rounded-full bg-[#F8FAFC]">
        <div
          class="h-full rounded-full bg-[#2563EB] transition-all duration-500"
          :style="{ width: `${clampedTurnout}%` }"
        />
      </div>
    </div>

    <VButton
      v-if="monitorRoute"
      class="min-h-touch w-full shrink-0 sm:w-auto sm:min-w-[10.5rem]"
      variant="secondary"
      @click="openControlRoom"
    >
      Open Control Room
    </VButton>
  </article>
</template>
