<script setup>
defineProps({
  report: { type: Object, default: null },
  loading: Boolean,
});
</script>

<template>
  <section class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5">
    <h3 class="text-lg font-semibold text-slate-900">Integrity report</h3>
    <p v-if="loading" class="mt-4 text-sm text-slate-500">Running verification checks…</p>
    <template v-else-if="report">
      <div
        class="mt-4 rounded-lg px-4 py-3 text-sm font-medium"
        :class="report.is_valid ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'"
      >
        {{ report.is_valid ? "All integrity checks passed" : "Integrity issues detected" }}
      </div>
      <ul v-if="report.blocking_issues?.length" class="mt-4 space-y-2">
        <li
          v-for="(issue, index) in report.blocking_issues"
          :key="index"
          class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {{ issue }}
        </li>
      </ul>
      <dl v-if="report.checks" class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div
          v-for="(check, key) in report.checks"
          :key="key"
          class="rounded-lg bg-slate-50 px-3 py-2 text-sm"
        >
          <dt class="font-medium capitalize text-slate-700">{{ String(key).replace(/_/g, " ") }}</dt>
          <dd :class="check.passed ? 'text-green-700' : 'text-red-700'">
            {{ check.passed ? "Passed" : "Failed" }}
          </dd>
        </div>
      </dl>
    </template>
    <p v-else class="mt-4 text-sm text-slate-500">Run integrity verification to see the report.</p>
  </section>
</template>
