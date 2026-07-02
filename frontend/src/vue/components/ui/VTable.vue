<script setup>
import { computed } from "vue";
import VPagination from "./VPagination.vue";

const props = defineProps({
  columns: {
    type: Array,
    default: () => [],
  },
  rows: {
    type: Array,
    default: () => [],
  },
  emptyText: {
    type: String,
    default: "No records found.",
  },
  loading: Boolean,
  scrollable: {
    type: Boolean,
    default: false,
  },
  page: { type: Number, default: null },
  totalPages: { type: Number, default: null },
  total: { type: Number, default: null },
  rangeLabel: { type: String, default: "" },
});

const emit = defineEmits(["row-click", "update:page"]);

const showPagination = computed(
  () => props.page != null && props.totalPages != null && props.total != null
);

function cellValue(row, column) {
  if (typeof column.accessor === "function") {
    return column.accessor(row);
  }
  return row[column.key];
}

function onPageChange(nextPage) {
  emit("update:page", nextPage);
}
</script>

<template>
  <div
    class="vb-table-shell"
    :class="scrollable ? 'vb-table-shell--scrollable flex min-h-0 flex-col' : ''"
  >
    <div v-if="loading" class="space-y-3 bg-white p-card">
      <div class="h-10 w-full animate-pulse rounded-input bg-slate-100" />
      <div
        v-for="n in 5"
        :key="n"
        class="h-table-row w-full animate-pulse rounded-input bg-slate-100"
      />
    </div>

    <div
      v-else-if="rows.length === 0"
      class="bg-white p-card text-center text-sm text-slate-500"
    >
      {{ emptyText }}
    </div>

    <template v-else>
      <div
        v-if="scrollable"
        class="vb-table-scroll min-h-0 flex-1 overflow-x-auto overflow-y-auto"
      >
        <table class="min-w-full divide-y divide-border">
          <thead class="sticky top-0 z-10 border-b border-border bg-surface-muted">
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
                scope="col"
                class="h-table-row px-4 text-left text-xs font-semibold uppercase tracking-wide text-ink-secondary"
              >
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr
              v-for="(row, index) in rows"
              :key="row.id || row.uuid || index"
              class="h-table-row transition hover:bg-surface-muted"
              @click="$emit('row-click', row)"
            >
              <td
                v-for="column in columns"
                :key="column.key"
                class="whitespace-nowrap px-4 text-sm text-slate-700"
              >
                <slot :name="`cell-${column.key}`" :row="row" :value="cellValue(row, column)">
                  {{ cellValue(row, column) }}
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="hidden overflow-x-auto md:block">
        <table class="min-w-full divide-y divide-border">
          <thead class="sticky top-0 z-10 border-b border-border bg-surface-muted">
            <tr>
              <th
                v-for="column in columns"
                :key="column.key"
                scope="col"
                class="h-table-row px-4 text-left text-xs font-semibold uppercase tracking-wide text-ink-secondary"
              >
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border bg-white">
            <tr
              v-for="(row, index) in rows"
              :key="row.id || row.uuid || index"
              class="h-table-row transition hover:bg-surface-muted"
              @click="$emit('row-click', row)"
            >
              <td
                v-for="column in columns"
                :key="column.key"
                class="whitespace-nowrap px-4 text-sm text-slate-700"
              >
                <slot :name="`cell-${column.key}`" :row="row" :value="cellValue(row, column)">
                  {{ cellValue(row, column) }}
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div
        v-if="!scrollable"
        class="space-y-3 p-4 md:hidden"
      >
        <article
          v-for="(row, index) in rows"
          :key="row.id || row.uuid || index"
          class="rounded-input border border-border bg-white p-4 shadow-sm"
          @click="$emit('row-click', row)"
        >
          <dl class="space-y-2">
            <div v-for="column in columns" :key="column.key" class="flex justify-between gap-4">
              <dt class="text-xs font-medium uppercase text-slate-500">{{ column.label }}</dt>
              <dd class="text-right text-sm text-slate-800">
                <slot :name="`cell-${column.key}`" :row="row" :value="cellValue(row, column)">
                  {{ cellValue(row, column) }}
                </slot>
              </dd>
            </div>
          </dl>
        </article>
      </div>

      <div
        v-else
        class="space-y-3 overflow-y-auto p-4 md:hidden"
      >
        <article
          v-for="(row, index) in rows"
          :key="row.id || row.uuid || index"
          class="rounded-input border border-border bg-white p-4 shadow-sm"
          @click="$emit('row-click', row)"
        >
          <dl class="space-y-2">
            <div v-for="column in columns" :key="column.key" class="flex justify-between gap-4">
              <dt class="text-xs font-medium uppercase text-slate-500">{{ column.label }}</dt>
              <dd class="text-right text-sm text-slate-800">
                <slot :name="`cell-${column.key}`" :row="row" :value="cellValue(row, column)">
                  {{ cellValue(row, column) }}
                </slot>
              </dd>
            </div>
          </dl>
        </article>
      </div>
    </template>

    <VPagination
      v-if="showPagination && !loading"
      :page="page"
      :total-pages="totalPages"
      :total="total"
      :range-label="rangeLabel"
      :disabled="loading"
      @update:page="onPageChange"
    />
  </div>
</template>
