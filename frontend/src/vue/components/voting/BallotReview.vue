<script setup>
defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  electionTitle: String,
});

const emit = defineEmits(["edit"]);
</script>

<template>
  <section class="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-900/5">
    <header class="mb-6">
      <h3 class="text-lg font-semibold text-slate-900">Review your ballot</h3>
      <p v-if="electionTitle" class="mt-1 text-sm text-slate-500">{{ electionTitle }}</p>
      <p class="mt-2 text-sm text-slate-600">
        Confirm your selections before submitting. You can go back to change any position.
      </p>
    </header>

    <ul class="space-y-4">
      <li
        v-for="item in items"
        :key="item.position.uuid"
        class="rounded-lg border border-slate-100 bg-slate-50/60 px-4 py-4"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="font-medium text-slate-900">{{ item.position.title }}</p>
            <ul class="mt-2 space-y-1">
              <li
                v-for="candidate in item.candidates"
                :key="candidate.uuid"
                class="text-sm text-slate-700"
              >
                {{ candidate.full_name }}
                <span v-if="candidate.department" class="text-slate-500">
                  — {{ candidate.department }}
                </span>
              </li>
            </ul>
            <p v-if="!item.candidates.length" class="mt-2 text-sm text-red-600">
              No selection — go back to choose a candidate.
            </p>
          </div>
          <button
            type="button"
            class="text-sm font-medium text-brand-600 hover:text-brand-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600"
            @click="emit('edit', item.position.uuid)"
          >
            Edit
          </button>
        </div>
      </li>
    </ul>
  </section>
</template>
