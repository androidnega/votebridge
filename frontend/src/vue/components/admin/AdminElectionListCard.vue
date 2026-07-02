<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { ElectionStatusBadge } from "@/components/voting";
import { FaIcon } from "@/components/ui";
import { getAdminSoftPalette } from "@/config/adminWorkspace";

const props = defineProps({
  election: { type: Object, required: true },
});

const router = useRouter();

const status = computed(() => props.election.status || props.election.election_status || "draft");
const title = computed(() => props.election.title || props.election.election_title || "Untitled election");

const paletteKey = computed(() => {
  const map = { open: "turnout", scheduled: "readiness", draft: "elections", paused: "tasks", closed: "results", archived: "neutral" };
  return map[status.value] || "neutral";
});

const palette = computed(() => getAdminSoftPalette(paletteKey.value));

function formatDate(value) {
  if (!value) return null;
  return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function open() {
  if (!props.election.uuid) return;
  router.push(`/dashboard/elections/${props.election.uuid}`);
}
</script>

<template>
  <button
    type="button"
    class="flex w-full flex-col rounded-card border p-4 text-left shadow-card transition hover:brightness-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
    :style="{ backgroundColor: palette.bg, borderColor: palette.border }"
    @click="open"
  >
    <div class="flex items-start gap-3">
      <div
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl shadow-sm"
        :style="{ backgroundColor: palette.iconBg, color: palette.icon }"
        aria-hidden="true"
      >
        <FaIcon icon="fa-check-to-slot" :fixed-width="false" class="text-lg" />
      </div>

      <div class="min-w-0 flex-1">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <h3 class="truncate text-sm font-semibold text-slate-900">{{ title }}</h3>
            <p v-if="election.start_date" class="mt-1 text-xs text-slate-600">
              {{ formatDate(election.start_date) }}
              <span v-if="election.end_date"> — {{ formatDate(election.end_date) }}</span>
            </p>
            <p v-if="election.election_type_display" class="mt-1 text-xs capitalize text-slate-500">
              {{ election.election_type_display }}
            </p>
          </div>
          <ElectionStatusBadge :status="status" size="sm" />
        </div>
      </div>
    </div>

    <div class="mt-4 flex items-center justify-between gap-2 border-t pt-3" :style="{ borderColor: palette.border }">
      <span class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600">
        <FaIcon icon="fa-check-to-slot" class="text-[11px] opacity-75" />
        Open workspace
      </span>
      <FaIcon icon="fa-chevron-right" class="text-xs text-slate-400" />
    </div>
  </button>
</template>
