<script setup>
import { computed } from "vue";
import VButton from "./VButton.vue";

const props = defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  total: { type: Number, default: 0 },
  rangeLabel: { type: String, default: "" },
  disabled: Boolean,
});

const emit = defineEmits(["update:page"]);

const showPager = computed(() => props.totalPages > 1);

function goTo(nextPage) {
  if (props.disabled) return;
  emit("update:page", nextPage);
}
</script>

<template>
  <div
    v-if="total > 0"
    class="flex flex-col gap-3 border-t border-border bg-surface-muted/40 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
  >
    <p class="text-xs text-ink-secondary">
      {{ rangeLabel || `${total} items` }}
    </p>
    <div v-if="showPager" class="flex items-center justify-end gap-2">
      <VButton
        size="sm"
        variant="secondary"
        :disabled="disabled || page <= 1"
        @click="goTo(page - 1)"
      >
        Previous
      </VButton>
      <span class="min-w-[4.5rem] text-center text-xs font-medium tabular-nums text-ink-primary">
        Page {{ page }} / {{ totalPages }}
      </span>
      <VButton
        size="sm"
        variant="secondary"
        :disabled="disabled || page >= totalPages"
        @click="goTo(page + 1)"
      >
        Next
      </VButton>
    </div>
  </div>
</template>
