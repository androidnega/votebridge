import { computed, ref, watch } from "vue";

export function useClientListPagination(sourceItems, { pageSize: initialPageSize = 15 } = {}) {
  const page = ref(1);
  const pageSize = ref(initialPageSize);

  const total = computed(() => sourceItems.value?.length || 0);
  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value) || 1));

  const items = computed(() => {
    const all = sourceItems.value || [];
    const start = (page.value - 1) * pageSize.value;
    return all.slice(start, start + pageSize.value);
  });

  const rangeLabel = computed(() => {
    if (!total.value) return "0 items";
    const start = (page.value - 1) * pageSize.value + 1;
    const end = Math.min(page.value * pageSize.value, total.value);
    return `${start}–${end} of ${total.value}`;
  });

  function goToPage(nextPage) {
    page.value = Math.min(Math.max(1, nextPage), totalPages.value);
  }

  watch([total, pageSize], () => {
    if (page.value > totalPages.value) {
      page.value = totalPages.value;
    }
  });

  watch(sourceItems, () => {
    page.value = 1;
  });

  return {
    page,
    pageSize,
    total,
    totalPages,
    rangeLabel,
    items,
    goToPage,
  };
}
