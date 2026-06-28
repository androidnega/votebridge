<script setup>
defineProps({
  report: { type: Object, default: null },
  loading: Boolean,
});
</script>

<template>
  <section class="rounded-xl bg-white p-card shadow-sm ring-1 ring-border">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h3 class="text-lg font-semibold text-slate-900">Election readiness</h3>
        <p class="mt-1 text-sm text-slate-500">
          Pre-open validation checklist — all critical checks must pass before opening.
        </p>
      </div>
      <div
        v-if="report && !loading"
        class="rounded-lg px-4 py-2 text-center"
        :class="report.is_ready ? 'bg-success-50 text-success-700' : 'bg-danger-50 text-danger-700'"
      >
        <p class="text-xs font-medium uppercase tracking-wide">Readiness score</p>
        <p class="text-2xl font-bold">{{ report.readiness_score }}%</p>
      </div>
    </div>

    <p v-if="loading" class="mt-4 text-sm text-slate-500">Running readiness checks…</p>

    <template v-else-if="report">
      <div
        class="mt-4 rounded-lg px-4 py-3 text-sm font-medium"
        :class="report.is_ready ? 'bg-success-50 text-success-800' : 'bg-danger-50 text-danger-800'"
      >
        {{
          report.is_ready
            ? "Election is ready to open"
            : "Critical readiness issues must be resolved before opening"
        }}
      </div>

      <ul v-if="report.blocking_issues?.length" class="mt-4 space-y-2">
        <li
          v-for="(issue, index) in report.blocking_issues"
          :key="`block-${index}`"
          class="rounded-lg bg-danger-50 px-3 py-2 text-sm text-danger-700"
        >
          {{ issue }}
        </li>
      </ul>

      <ul v-if="report.warnings?.length" class="mt-4 space-y-2">
        <li
          v-for="(warning, index) in report.warnings"
          :key="`warn-${index}`"
          class="rounded-lg bg-warning-50 px-3 py-2 text-sm text-warning-800"
        >
          {{ warning }}
        </li>
      </ul>

      <dl v-if="report.checks" class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div
          v-for="(check, key) in report.checks"
          :key="key"
          class="rounded-lg bg-surface-muted px-3 py-2 text-sm"
        >
          <dt class="font-medium text-slate-700">{{ check.label || String(key).replace(/_/g, " ") }}</dt>
          <dd :class="check.passed ? 'text-success-700' : check.critical ? 'text-danger-700' : 'text-warning-700'">
            {{ check.passed ? "Passed" : "Failed" }}
            <span v-if="check.message" class="mt-1 block text-xs font-normal text-slate-600">
              {{ check.message }}
            </span>
          </dd>
        </div>
      </dl>

      <p v-if="report.validated_at" class="mt-4 text-xs text-slate-500">
        Last validated {{ new Date(report.validated_at).toLocaleString() }}
      </p>
    </template>

    <p v-else class="mt-4 text-sm text-slate-500">Run readiness validation to see the report.</p>
  </section>
</template>
