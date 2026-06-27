<script setup>
defineProps({
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
});

defineEmits(["row-click"]);

function cellValue(row, column) {
  if (typeof column.accessor === "function") {
    return column.accessor(row);
  }
  return row[column.key];
}
</script>

<template>
  <div class="overflow-hidden rounded-card ring-1 ring-slate-900/5">
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

    <div v-else class="hidden overflow-x-auto md:block">
      <table class="min-w-full divide-y divide-border">
        <thead class="sticky top-0 z-10 bg-slate-50">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              scope="col"
              class="h-table-row px-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border bg-white">
          <tr
            v-for="(row, index) in rows"
            :key="row.id || row.uuid || index"
            class="h-table-row transition hover:bg-slate-50/80"
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

    <div v-if="!loading && rows.length" class="space-y-3 p-4 md:hidden">
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
  </div>
</template>
