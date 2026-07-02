<script setup>
import { computed, ref } from "vue";
import { StatusBadge } from "@/components/ui";

const props = defineProps({
  rows: { type: Array, default: () => [] },
});

defineEmits(["select"]);

const tabs = [
  { id: "all", label: "All" },
  { id: "open", label: "Open" },
  { id: "scheduled", label: "Scheduled" },
  { id: "closed", label: "Closed" },
];

const activeTab = ref("all");

const filteredRows = computed(() => {
  if (activeTab.value === "all") return props.rows;
  if (activeTab.value === "open") {
    return props.rows.filter((row) => ["open", "paused"].includes(row.status));
  }
  return props.rows.filter((row) => row.status === activeTab.value);
});
</script>

<template>
  <section class="overflow-hidden rounded-card border border-border bg-white shadow-[0_1px_3px_0_rgb(15_23_42_/_0.06)]">
    <header class="flex flex-col gap-4 border-b border-border px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
      <div>
        <h3 class="text-lg font-semibold text-ink-primary">All elections</h3>
        <p class="mt-1 text-sm text-ink-secondary">Monitor lifecycle, turnout, and ballot setup at a glance.</p>
      </div>
      <div class="flex flex-wrap gap-1 rounded-input bg-surface-muted p-1">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="rounded-[8px] px-3 py-1.5 text-xs font-semibold transition"
          :class="
            activeTab === tab.id
              ? 'bg-white text-brand-700 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          "
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
    </header>

    <div class="overflow-x-auto">
      <table class="min-w-full text-left text-sm">
        <thead class="border-b border-border bg-surface-muted/80 text-xs font-semibold uppercase tracking-wide text-slate-500">
          <tr>
            <th class="px-5 py-3 sm:px-6">Election</th>
            <th class="px-3 py-3">Status</th>
            <th class="px-3 py-3">Turnout</th>
            <th class="hidden px-3 py-3 md:table-cell">Positions</th>
            <th class="hidden px-3 py-3 lg:table-cell">Candidates</th>
            <th class="px-5 py-3 sm:px-6" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in filteredRows"
            :key="row.uuid"
            class="border-b border-border/80 transition hover:bg-surface-muted/50"
          >
            <td class="px-5 py-4 sm:px-6">
              <div class="flex items-center gap-3">
                <span
                  class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-bold text-brand-700"
                >
                  {{ index + 1 }}
                </span>
                <div class="min-w-0">
                  <p class="truncate font-medium text-ink-primary">{{ row.title }}</p>
                  <p class="text-xs text-ink-secondary">{{ row.dateLabel }}</p>
                </div>
              </div>
            </td>
            <td class="px-3 py-4">
              <StatusBadge :status="row.status" />
            </td>
            <td class="px-3 py-4 tabular-nums font-medium text-ink-primary">
              {{ row.turnoutLabel }}
            </td>
            <td class="hidden px-3 py-4 tabular-nums text-ink-secondary md:table-cell">
              {{ row.position_count ?? "—" }}
            </td>
            <td class="hidden px-3 py-4 tabular-nums text-ink-secondary lg:table-cell">
              {{ row.approved_candidate_count ?? 0 }} / {{ row.candidate_count ?? 0 }}
            </td>
            <td class="px-5 py-4 text-right sm:px-6">
              <button
                type="button"
                class="text-sm font-semibold text-brand-700 hover:underline"
                @click="$emit('select', row.uuid)"
              >
                Open
              </button>
            </td>
          </tr>
          <tr v-if="!filteredRows.length">
            <td colspan="6" class="px-6 py-10 text-center text-sm text-ink-secondary">
              No elections match this filter.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
