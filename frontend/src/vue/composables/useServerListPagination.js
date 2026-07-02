import { computed, ref, watch } from "vue";

export function useServerListPagination(fetchPage, { pageSize: initialPageSize = 15 } = {}) {
  const page = ref(1);
  const pageSize = ref(initialPageSize);
  const total = ref(0);
  const items = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value) || 1));

  const rangeLabel = computed(() => {
    if (!total.value) return "0 items";
    const start = (page.value - 1) * pageSize.value + 1;
    const end = Math.min(page.value * pageSize.value, total.value);
    return `${start}–${end} of ${total.value}`;
  });

  async function load() {
    loading.value = true;
    error.value = null;
    try {
      const result = await fetchPage({
        page: page.value,
        page_size: pageSize.value,
      });
      items.value = result.items || [];
      total.value = result.count ?? items.value.length;
      if (page.value > totalPages.value) {
        page.value = totalPages.value;
        if (page.value > 1) {
          return load();
        }
      }
    } catch (err) {
      error.value = err;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function goToPage(nextPage) {
    const target = Math.min(Math.max(1, nextPage), totalPages.value);
    if (target === page.value) return;
    page.value = target;
    await load();
  }

  watch(pageSize, () => {
    page.value = 1;
    load().catch(() => {});
  });

  return {
    page,
    pageSize,
    total,
    totalPages,
    rangeLabel,
    items,
    loading,
    error,
    load,
    goToPage,
    refresh: load,
  };
}
