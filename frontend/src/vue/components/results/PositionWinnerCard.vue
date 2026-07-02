<script setup>
import { computed } from "vue";
import VIcon from "@/components/ui/VIcon.vue";
import { getPositionResultPalette } from "@/config/positionResultPalettes";
import { getCandidatePhotoUrl } from "@/utils/candidateDisplay";

const props = defineProps({
  position: { type: Object, required: true },
});

const winners = computed(() => (props.position.candidates || []).filter((candidate) => candidate.is_winner));

const primaryWinner = computed(() => winners.value[0] || null);

const photoUrl = computed(() => (primaryWinner.value ? getCandidatePhotoUrl(primaryWinner.value) : null));

const palette = computed(() =>
  getPositionResultPalette(props.position.position_title, props.position.display_order)
);

const cardStyle = computed(() => ({
  backgroundColor: palette.value.bg,
  borderColor: palette.value.border,
}));

const badgeStyle = computed(() => ({
  backgroundColor: palette.value.badge,
}));

const positionLabelStyle = computed(() => ({
  color: palette.value.accent,
}));

const voteLabel = computed(() => {
  if (!primaryWinner.value) return "—";
  const count = primaryWinner.value.vote_count ?? 0;
  const pct = primaryWinner.value.vote_percentage ?? 0;
  return `${count} vote${count === 1 ? "" : "s"} · ${pct}%`;
});
</script>

<template>
  <article
    class="flex h-full flex-col overflow-hidden rounded-xl border shadow-sm"
    :style="cardStyle"
  >
    <div
      class="relative mx-auto aspect-square w-full max-w-full overflow-hidden"
      :style="{ boxShadow: `inset 0 0 0 2px ${palette.photoRing}` }"
    >
      <img
        v-if="photoUrl"
        :src="photoUrl"
        :alt="`${primaryWinner?.full_name || 'Winner'} photo`"
        class="block aspect-square h-full w-full object-cover object-[50%_20%]"
      />
      <div
        v-else
        class="flex aspect-square h-full w-full items-center justify-center bg-white/60 text-slate-400"
        aria-hidden="true"
      >
        <VIcon name="profile" size="sm" />
      </div>
      <span
        class="absolute left-1.5 top-1.5 rounded-full px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-white shadow-sm"
        :style="badgeStyle"
      >
        Winner
      </span>
    </div>

    <div class="flex flex-1 flex-col border-t p-2.5 text-center sm:p-3" :style="{ borderColor: palette.border }">
      <p class="text-[10px] font-semibold uppercase tracking-wide" :style="positionLabelStyle">
        {{ position.position_title }}
      </p>
      <template v-if="primaryWinner">
        <h3 class="mt-1 text-sm font-semibold leading-snug text-slate-900">{{ primaryWinner.full_name }}</h3>
        <p v-if="primaryWinner.department" class="mt-0.5 line-clamp-2 text-[11px] leading-tight text-slate-600">
          {{ primaryWinner.department }}
        </p>
        <p class="mt-2 text-[11px] font-medium tabular-nums text-slate-700">{{ voteLabel }}</p>
      </template>
      <p v-else class="mt-1 text-xs text-slate-500">No votes recorded</p>

      <ul
        v-if="winners.length > 1"
        class="mt-2 space-y-0.5 border-t pt-2 text-left text-[11px] text-slate-600"
        :style="{ borderColor: palette.border }"
      >
        <li v-for="candidate in winners.slice(1)" :key="candidate.candidate_uuid">
          {{ candidate.full_name }}
          <span class="text-slate-400">· {{ candidate.vote_count }}</span>
        </li>
      </ul>
    </div>
  </article>
</template>
