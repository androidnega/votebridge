<script setup>
defineProps({
  position: { type: Object, required: true },
  showWinners: { type: Boolean, default: true },
});
</script>

<template>
  <article class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5">
    <header class="mb-4 flex flex-wrap items-start justify-between gap-2">
      <div>
        <h3 class="text-lg font-semibold text-slate-900">{{ position.position_title }}</h3>
        <p class="text-sm text-slate-500">{{ position.total_ballots ?? 0 }} votes cast</p>
      </div>
      <span
        v-if="showWinners && position.winners?.length"
        class="rounded-full bg-green-50 px-2.5 py-0.5 text-xs font-medium text-green-700 ring-1 ring-green-200"
      >
        {{ position.winners.length }} winner{{ position.winners.length > 1 ? "s" : "" }}
      </span>
    </header>

    <ul class="space-y-3">
      <li
        v-for="candidate in position.candidates || []"
        :key="candidate.candidate_uuid"
        class="rounded-lg border px-4 py-3"
        :class="candidate.is_winner ? 'border-green-200 bg-green-50/50' : 'border-slate-100 bg-slate-50/40'"
      >
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="font-medium text-slate-900">
              {{ candidate.full_name }}
              <span v-if="candidate.is_winner" class="ml-2 text-xs font-semibold text-green-700">Winner</span>
            </p>
            <p v-if="candidate.department" class="text-sm text-slate-500">{{ candidate.department }}</p>
          </div>
          <div class="text-right">
            <p class="text-lg font-semibold tabular-nums text-slate-900">{{ candidate.vote_count }}</p>
            <p class="text-xs text-slate-500">{{ candidate.vote_percentage }}%</p>
          </div>
        </div>
        <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200">
          <div
            class="h-full rounded-full bg-brand-600 transition-all"
            :style="{ width: `${candidate.vote_percentage || 0}%` }"
          />
        </div>
      </li>
    </ul>
  </article>
</template>
