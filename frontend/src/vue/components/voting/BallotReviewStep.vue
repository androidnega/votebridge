<script setup>
import { computed } from "vue";

const props = defineProps({
  reviewItems: { type: Array, default: () => [] },
  skippedCount: { type: Number, default: 0 },
  submitting: { type: Boolean, default: false },
});

const emit = defineEmits(["back", "submit", "edit"]);

const hasSelections = computed(() =>
  props.reviewItems.some((item) => item.candidates?.length)
);
</script>

<template>
  <section>
    <header class="mb-6">
      <h2 class="text-2xl font-bold text-ink-primary">Review Your Ballot</h2>
      <p class="mt-2 text-sm text-ink-secondary">
        Confirm your choices before final submission. You may go back to change any position.
      </p>
    </header>

    <ul class="divide-y divide-border rounded-lg border border-border bg-surface">
      <li
        v-for="item in reviewItems"
        :key="item.position.uuid"
        class="flex items-start justify-between gap-3 px-4 py-3"
      >
        <div class="min-w-0">
          <p class="text-sm font-semibold text-ink-primary">{{ item.position.title }}</p>
          <p v-if="item.candidates.length" class="mt-1 text-sm text-success-700">
            ✓ {{ item.candidates.map((c) => c.full_name).join(", ") }}
          </p>
          <p v-else class="mt-1 text-sm text-ink-secondary">Not selected</p>
        </div>
        <button
          type="button"
          class="shrink-0 text-xs font-medium text-brand-700 hover:text-brand-800"
          @click="emit('edit', item.position.uuid)"
        >
          Edit
        </button>
      </li>
    </ul>

    <p v-if="skippedCount > 0" class="mt-4 text-sm text-ink-secondary">
      You have skipped {{ skippedCount }} position{{ skippedCount === 1 ? "" : "s" }}.
      You may return to complete them or submit your ballot as it is.
    </p>

    <div class="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
      <button
        type="button"
        class="min-h-[48px] text-sm font-medium text-ink-secondary hover:text-ink-primary"
        :disabled="submitting"
        @click="emit('back')"
      >
        Back
      </button>
      <button
        type="button"
        class="min-h-[48px] rounded-lg bg-brand-700 px-6 text-sm font-semibold text-white hover:bg-brand-800 disabled:opacity-50"
        :disabled="submitting || !hasSelections"
        @click="emit('submit')"
      >
        {{ submitting ? "Submitting…" : "Submit Ballot" }}
      </button>
    </div>
  </section>
</template>
