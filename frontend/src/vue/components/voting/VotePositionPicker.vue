<script setup>
defineProps({
  positions: { type: Array, default: () => [] },
  electionTitle: { type: String, default: "" },
});

defineEmits(["select", "back"]);
</script>

<template>
  <section class="w-full" aria-labelledby="position-picker-heading">
    <header class="mb-6">
      <p class="text-xs font-semibold uppercase tracking-wide text-brand-700">Token verified</p>
      <h2 id="position-picker-heading" class="mt-1 text-2xl font-bold text-ink-primary">
        Select a position
      </h2>
      <p class="mt-2 text-sm text-ink-secondary">
        Choose the office you want to vote for in {{ electionTitle || "this election" }}.
      </p>
    </header>

    <ul class="grid gap-3 sm:grid-cols-2" role="list">
      <li v-for="position in positions" :key="position.uuid">
        <button
          type="button"
          class="group flex w-full items-center justify-between rounded-card border border-border bg-surface px-5 py-4 text-left shadow-card transition hover:border-brand-300 hover:shadow-card-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-700"
          @click="$emit('select', position.uuid)"
        >
          <div class="min-w-0">
            <p class="font-semibold text-ink-primary">{{ position.title }}</p>
            <p class="mt-0.5 text-sm text-ink-secondary">
              {{ position.candidates?.length || 0 }} candidate{{
                (position.candidates?.length || 0) === 1 ? "" : "s"
              }}
            </p>
          </div>
          <span
            class="ml-3 shrink-0 text-sm font-medium text-brand-700 transition group-hover:translate-x-0.5"
            aria-hidden="true"
          >
            Vote →
          </span>
        </button>
      </li>
    </ul>

    <button
      type="button"
      class="mt-6 text-sm font-medium text-ink-secondary transition hover:text-ink-primary"
      @click="$emit('back')"
    >
      ← Back to my elections
    </button>
  </section>
</template>
