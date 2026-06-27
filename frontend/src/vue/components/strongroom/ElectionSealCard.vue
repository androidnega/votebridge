<script setup>
defineProps({
  status: { type: String, default: "pending" },
  sealedAt: String,
  lockedAt: String,
  verificationHash: String,
});

const statusClasses = {
  pending: "bg-slate-100 text-slate-700",
  sealed: "bg-indigo-50 text-indigo-700",
  locked: "bg-green-50 text-green-700",
};
</script>

<template>
  <article class="rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-900/5">
    <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Election seal</p>
    <div class="mt-2 flex flex-wrap items-center gap-2">
      <span
        class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium capitalize"
        :class="statusClasses[status] || statusClasses.pending"
      >
        {{ status }}
      </span>
    </div>
    <dl class="mt-4 space-y-2 text-sm">
      <div v-if="sealedAt">
        <dt class="text-slate-500">Sealed</dt>
        <dd class="font-medium text-slate-900">{{ new Date(sealedAt).toLocaleString() }}</dd>
      </div>
      <div v-if="lockedAt">
        <dt class="text-slate-500">Locked</dt>
        <dd class="font-medium text-slate-900">{{ new Date(lockedAt).toLocaleString() }}</dd>
      </div>
      <div v-if="verificationHash">
        <dt class="text-slate-500">Public verification hash</dt>
        <dd class="break-all font-mono text-xs text-slate-700">{{ verificationHash }}</dd>
      </div>
    </dl>
  </article>
</template>
